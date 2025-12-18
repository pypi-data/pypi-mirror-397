import math
import os
from datetime import datetime

import numpy as np
import torch
from sklearn.metrics import f1_score
from torch.utils.tensorboard import SummaryWriter
from tqdm import tqdm


def clip_grad_norm(model, clip_grad_val=1):
    torch.nn.utils.clip_grad_norm_(model.parameters(), clip_grad_val)


class GradNormClipper:

    def __init__(self, clip_val):
        self.clip_val = clip_val

    def __call__(self, model):
        torch.nn.utils.clip_grad_norm_(model.parameters(), self.clip_val)



def f1(output, labels):
    pred_labels = torch.argmax(output, dim=1)

    return f1_score(labels, pred_labels, labels=None, average='weighted', sample_weight=None,
                             zero_division='warn')

class Trainer:
    """TODO DO AGGRESSIVBE VERSION"""
    def __init__(self, optimizer, model, loss_fn,  grad_f=None, score_function=f1, score_name="f1", score_direction=1, scheduler=None):
        self.optimizer = optimizer
        self.model = model
        self.loss_fn = loss_fn
        self.grad_f = grad_f

        self.score_direction = score_direction

        self.writer = None

        self.score_function = score_function
        self.score_name = score_name

        self.scheduler = scheduler

    def _epoch(self, loader, epoch_index, report_frequency, device="cpu"):

        """
        :param loader:
        :param epoch_index:
        :param report_frequency:
        :param device: device to move tensors to. None for do nothing
        :return:
        """

        # Make sure gradient tracking is on, and do a pass over the data
        self.model.train(True)

        running_loss = 0.
        last_loss = 0.
        with tqdm(total=len(loader),desc="Batch") as pbar:
            for i, data in enumerate(loader):
                # Every data instance is an input + label pair

                inputs, labels = data
                if device is not None:
                    if isinstance(inputs, (list, tuple)):
                        inputs = map(lambda x: x.to(device, non_blocking=True), inputs)
                    else:
                        inputs = inputs.to(device, non_blocking=True)

                    labels = labels.to(device, non_blocking=True)


                #Zero your gradients for every batch
                self.optimizer.zero_grad()

                # Make predictions for this batch
                outputs = self.model(*inputs)

                # Compute the loss and its gradients
                loss = self.loss_fn(outputs, labels)
                loss.backward()

                # clip the gradient
                if self.grad_f is not None:
                    self.grad_f(self.model)

                # Adjust learning weights
                self.optimizer.step()

                if self.scheduler is not None:
                    self.scheduler.step()

                # Gather data and report
                running_loss += loss.item()
                if i % report_frequency == report_frequency - 1:
                    pbar.set_postfix({'Batch ': i + 1,
                                      'Last loss': last_loss,
                                      }, refresh=False)
                    pbar.update(report_frequency)

                    last_loss = running_loss / report_frequency  # loss per item
                    #print('  batch {} loss: {}'.format(i + 1, last_loss))
                    tb_x = epoch_index * len(loader) + i + 1
                    self.writer.add_scalar('Loss/train', last_loss, tb_x)
                    running_loss = 0.

        return last_loss

    def _validate(self, validation_loader, device, sample_out=False):

        self.model.train(False)

        running_vloss = 0.0
        running_score = 0.0

        pred_validation=[]
        label_validation=[]

        for i, vdata in enumerate(validation_loader):
            vinputs, vlabels = vdata

            if device is not None:
                if isinstance(vinputs, (list, tuple)):
                    vinputs = map(lambda x: x.to(device, non_blocking=True), vinputs)

                else:
                    vinputs = vinputs.to(device, non_blocking=True)

                vlabels = vlabels.to(device, non_blocking=True)



            voutputs = self.model(*vinputs)
            vloss = self.loss_fn(voutputs, vlabels)
            running_vloss += vloss.item()

            pred_validation.append(voutputs.cpu().detach().numpy())
            label_validation.append(vlabels.cpu().detach().numpy())

            vf1 = self.score_function(voutputs.cpu(), vlabels.cpu())
            running_score += vf1

        avg_vloss = running_vloss / (i + 1)
        avg_score = running_score / (i + 1)
        # print('LOSS train {} valid {}'.format(avg_loss, avg_vloss))
        # print('Weighted avg f1 {}'.format(avg_f1))
        if not sample_out:
            return  avg_vloss, avg_score
        else:
            return avg_vloss, avg_score, np.concatenate(label_validation,axis=0), np.concatenate(pred_validation,axis=0)

    def train(self, epochs, training_loader, test_loader, validation_loader=None, report_per_epoch=10,
              writer_base_path="runs", model_base_path=".", model_tag="model", device="cpu", validation_path=None):
        # Initializing in a separate cell so we can easily add more epochs to the same run
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.writer = SummaryWriter(f"{writer_base_path}/{model_tag}_{timestamp}")

        model_name = f"{model_tag}_{timestamp}"
        base_dir = f"{model_base_path}/{model_name}"
        os.mkdir(base_dir)

        n_batch = len(training_loader)

        report_frequency = math.ceil(n_batch / report_per_epoch)

        best_score_epoch = 0.
        if self.score_direction == -1:
            best_score = 1_000_000
        else:
            best_score = 0


        best_vloss = 1_000_000.
        best_vloss_epoch = 0

        best_vloss_val = 1_000_000.

        best_epoch = 0

        model_path = None

        with tqdm(total=epochs, desc='Epoch') as pbar:
            for epoch in range(epochs):

                #print('EPOCH {}:'.format(epoch_number + 1))
                avg_loss = self._epoch(training_loader, epoch, report_frequency, device)

                # We don't need gradients on to do reporting

                avg_vloss, avg_score = self._validate(test_loader, device)

                if validation_loader is not None:
                    avg_vloss_val, avg_score, sample_label, sample_output = self._validate(validation_loader, device, sample_out=True)


                # Log the running loss averaged per batch
                # for both training and validation
                self.writer.add_scalars('Training vs. Validation Loss',
                                        {'Training': avg_loss, 'test': avg_vloss, "validation": avg_vloss_val},
                                        epoch + 1)

                self.writer.add_scalars(f'Weighted avg {self.score_name}',
                                        {f'Weighted avg {self.score_name}': avg_score},
                                        epoch + 1)

                # todo f1 for all v batch at once

                self.writer.flush()


                # Track the best performance, and save the model's state
                if avg_vloss < best_vloss:
                    best_vloss = avg_vloss
                    best_vloss_epoch = epoch + 1
                    best_epoch = best_vloss_epoch
                    best_metric = "loss"
                    model_path = f'{base_dir}/{best_metric}_{model_tag}_{timestamp}_{best_vloss_epoch}'
                    torch.save(self.model.state_dict(), model_path)

                if avg_vloss_val < best_vloss_val:
                    best_vloss_val = avg_vloss_val
                    best_vloss_val_epoch = epoch + 1

                    if validation_path is not None:
                        np.savetxt(f"{validation_path}_label_path.csv", sample_label, delimiter=",")
                        np.savetxt(f"{validation_path}_output_path.csv", sample_output, delimiter=",")


                if self.score_direction * avg_score > self.score_direction*best_score:
                    best_score = avg_score
                    best_score_epoch = epoch+1
                    best_epoch = best_score_epoch
                    best_metric = self.score_name
                    model_path = f'{base_dir}/{best_metric}_{model_tag}_{timestamp}_{best_score_epoch}'
                    torch.save(self.model.state_dict(), model_path)


                pbar.set_postfix({f'best {self.score_name} epoch': best_score_epoch,
                                  f'best {self.score_name}': best_score,
                                  f'current {self.score_name}': avg_score,
                                  'best avg loss epoch': best_vloss_epoch,
                                  'best avg loss': best_vloss,
                                  'current avg loss': avg_vloss,
                                  'best val loos': best_vloss_val,
                                  'best val epoch loos': best_vloss_val_epoch}, refresh=False)
                pbar.update(1)


        # load best model
        self.model.load_state_dict(torch.load(model_path))
        #switch off training
        self.model.train(False)
        # git model for inference

        vinputs, _ = next(iter(test_loader))

        if device is not None:
            if isinstance(vinputs, (list, tuple)):
                vinputs = list(map(lambda x: x.to(device), vinputs))
            else:
                vinputs = vinputs.to(device)

        # switch off gradient
        #todo update py torch
        #torch.jit.enable_onednn_fusion(True)
        with torch.inference_mode():
            #model_scripted = torch.jit.script(model, example_inputs=vinputs)  # Export to TorchScript, from the doc: TorchScript is actually the recommended model format for scaled inference and deployment.

            model_scripted = torch.jit.trace(self.model, example_inputs=vinputs)
            model_scripted = torch.jit.freeze(model_scripted)

            model_path = f'{base_dir}/jited_{best_metric}_{model_tag}_{timestamp}_{best_epoch}.pt'
            model_scripted.save(model_path)  # Save

        return base_dir, model_path, model_name



def train_one_epoch(loader, optimizer, scheduler, model , loss_fn, epoch_index, tb_writer, report_frequency, grad_f=None,
                    device="cpu"):
    """
    TODO DO AGGRESSIVBE VERSION
    :param loader:
    :param optimizer:
    :param model:
    :param loss_fn:
    :param epoch_index:
    :param tb_writer:
    :param report_frequency:
    :param grad_f:
    :param device: device to move tensors to. None for do nothing
    :return:
    """

    running_loss = 0.
    last_loss = 0.
    with tqdm(total=len(loader),desc="Batch") as pbar:
        for i, data in enumerate(loader):
            # Every data instance is an input + label pair
            inputs, labels = data

            if device is not None:
                if isinstance(inputs, (list, tuple)):
                    inputs = map(lambda x: x.to(device, non_blocking=True), inputs)
                else:
                    inputs = inputs.to(device, non_blocking=True) #create a tuple to match with list

                labels = labels.to(device, non_blocking=True)
            # Zero your gradients for every batch!
            optimizer.zero_grad()

            # Make predictions for this batch
            outputs = model(*inputs)

            del inputs

            # Compute the loss and its gradients
            loss = loss_fn(outputs, labels)
            loss.backward()

            # clip the gradient
            if grad_f is not None:
                grad_f(model)

            # Adjust learning weights
            optimizer.step()

            if scheduler is not None:
                scheduler.step()
            # Gather data and report
            running_loss += loss.item()
            if i % report_frequency == report_frequency - 1:
                pbar.set_postfix({'Batch ': i + 1,
                                  'Last loss': last_loss,
                                  }, refresh=False)
                pbar.update(report_frequency)

                last_loss = running_loss / report_frequency  # loss per item
                #print('  batch {} loss: {}'.format(i + 1, last_loss))
                tb_x = epoch_index * len(loader) + i + 1
                tb_writer.add_scalar('Loss/train', last_loss, tb_x)
                running_loss = 0.




    return last_loss

    # PyTorch TensorBoard support


def train(epochs, model, optimizer, loss_fn, scheduler, training_loader, validation_loader, report_per_epoch=10,
          writer_base_path="runs", model_base_path=".", model_tag="model", grad_f=None, device="cpu"):
    # Initializing in a separate cell so we can easily add more epochs to the same run
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    writer = SummaryWriter(f"{writer_base_path}/{model_tag}_{timestamp}")


    model_name = f"{model_tag}_{timestamp}"
    base_dir = f"{model_base_path}/{model_name}"
    os.mkdir(base_dir)

    n_batch = len(training_loader)

    report_frequency = math.ceil(n_batch / report_per_epoch)

    best_vloss = 1_000_000.
    model_path = None

    for epoch in range(epochs):
        #print('EPOCH {}:'.format(epoch + 1))

        # Make sure gradient tracking is on, and do a pass over the data
        model.train(True)
        avg_loss = train_one_epoch(training_loader, optimizer, scheduler, model, loss_fn, epoch, writer, report_frequency, grad_f,device)

        # We don't need gradients on to do reporting
        model.train(False)

        running_vloss = 0.0
        i=0
        for i, vdata in enumerate(validation_loader):
            vinputs, vlabels = vdata

            if device is not None:
                if isinstance(vinputs, (list, tuple)):
                    vinputs = map(lambda x: x.to(device, non_blocking=True), vinputs)
                else:
                    vinputs = vinputs.to(device, non_blocking=True)

                vlabels = vlabels.to(device, non_blocking=True)

            voutputs = model(*vinputs)
            vloss = loss_fn(voutputs, vlabels)
            running_vloss += vloss

        avg_vloss = running_vloss / (i + 1)
        #print('LOSS train {} valid {}'.format(avg_loss, avg_vloss))

        # Log the running loss averaged per batch
        # for both training and validation
        writer.add_scalars('Training vs. Validation Loss',
                           {'Training': avg_loss, 'Validation': avg_vloss},
                           epoch + 1)
        writer.flush()

        # Track the best performance, and save the model's state

        if avg_vloss < best_vloss:
            best_vloss = avg_vloss
            best_metric = "loss"
            model_path = f'{base_dir}/{best_metric}_{model_tag}_{timestamp}_{epoch}'
            torch.save(model.state_dict(), model_path)

        epoch += 1

    model.load_state_dict(torch.load(model_path))
    model.train(False)
    # git model for inference
    model_scripted = torch.jit.script(
        model)  # Export to TorchScript, from the doc: TorchScript is actually the recommended model format for scaled inference and deployment.
    model_path = f'{base_dir}/jited_{best_metric}_{model_tag}_{timestamp}_{epoch}.pt'
    model_scripted.save(model_path)  # Save

    return base_dir, model_path, model_name



def train_labeling(epochs, model, optimizer, loss_fn, scheduler, training_loader, validation_loader, report_per_epoch=10,
          writer_base_path="runs", model_base_path=".", model_tag="model", grad_f=None, device="cpu"):
    # Initializing in a separate cell so we can easily add more epochs to the same run
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    writer = SummaryWriter(f"{writer_base_path}/{model_tag}_{timestamp}")

    model_name = f"{model_tag}_{timestamp}"
    base_dir = f"{model_base_path}/{model_name}"
    os.makedirs(base_dir, exist_ok=True)

    n_batch = len(training_loader)

    report_frequency = math.ceil(n_batch / report_per_epoch)

    best_f1_epoch=0.
    best_f1 = 0.

    best_vloss = 1_000_000.
    best_vloss_epoch = 0

    best_epoch = 0



    model_path = None

    with tqdm(total=epochs, desc='Epoch') as pbar:
        for epoch in range(epochs):

            #print('EPOCH {}:'.format(epoch_number + 1))

            # Make sure gradient tracking is on, and do a pass over the data
            model.train(True)
            avg_loss = train_one_epoch(training_loader, optimizer, scheduler, model, loss_fn, epoch, writer, report_frequency, grad_f,device)

            # We don't need gradients on to do reporting
            model.train(False)

            running_vloss = 0.0
            running_vf1 = 0.0
            for i, vdata in enumerate(validation_loader):
                vinputs, vlabels = vdata

                if device is not None:
                    if isinstance(vinputs, (list, tuple)):
                        vinputs = map(lambda x: x.to(device, non_blocking=True), vinputs)
                    else:
                        vinputs = vinputs.to(device, non_blocking=True) #create a tuple to match with list

                    vlabels = vlabels.to(device, non_blocking=True)

                voutputs = model(*vinputs)

                del vinputs

                vloss = loss_fn(voutputs, vlabels)
                running_vloss += vloss.item()

                vf1 = f1(voutputs.cpu(), vlabels.cpu())
                running_vf1 += vf1

            avg_vloss = running_vloss / (i + 1)
            avg_f1 = running_vf1/ (i + 1)
            #print('LOSS train {} valid {}'.format(avg_loss, avg_vloss))
            #print('Weighted avg f1 {}'.format(avg_f1))

            # Log the running loss averaged per batch
            # for both training and validation
            writer.add_scalars('Training vs. Validation Loss',
                               {'Training': avg_loss, 'Validation': avg_vloss},
                               epoch + 1)
            writer.add_scalars('Weighted avg f1',
                               {'Weighted avg f1': avg_f1},
                               epoch + 1)

            # todo f1 for all v batch at once

            writer.flush()

            # Track the best performance, and save the model's state
            if avg_vloss < best_vloss:
                best_vloss = avg_vloss
                best_vloss_epoch = epoch + 1
                best_epoch = best_vloss_epoch
                best_metric = "loss"
                model_path = f'{base_dir}/{best_metric}_{model_tag}_{timestamp}_{best_vloss_epoch}_{int(1000*best_vloss)}'
                torch.save(model.state_dict(), model_path)

            if avg_f1 > best_f1:
                best_f1 = avg_f1
                best_f1_epoch = epoch+1
                best_epoch = best_f1_epoch
                best_metric = "f1"
                model_path = f'{base_dir}/{best_metric}_{model_tag}_{timestamp}_{best_f1_epoch}_{int(100*best_f1)}'
                torch.save(model.state_dict(), model_path)


            pbar.set_postfix({'best f1 epoch': best_f1_epoch,
                              'best f1': best_f1,
                              'current f1': avg_f1,
                              'best avg loss epoch': best_vloss_epoch,
                              'best avg loss': best_vloss,
                              'current avg loss': avg_vloss}, refresh=False)
            pbar.update(1)


    # load best model
    model.load_state_dict(torch.load(model_path))
    #switch off training
    model.train(False)
    # git model for inference

    vinputs, _ = next(iter(validation_loader))

    if device is not None:
        if isinstance(vinputs, (list, tuple)):
            vinputs = map(lambda x: x.to(device), vinputs)
        else:
            vinputs = vinputs.to(device)  # create a tuple to match with list


    # switch off gradient
    #todo update py torch
    #torch.jit.enable_onednn_fusion(True)
    with torch.inference_mode():
        #model_scripted = torch.jit.script(model, example_inputs=vinputs)  # Export to TorchScript, from the doc: TorchScript is actually the recommended model format for scaled inference and deployment.
        model_scripted = torch.jit.trace(model, example_inputs=vinputs)
        model_scripted = torch.jit.freeze(model_scripted)

        model_path_jitted = f'{base_dir}/jited_{best_metric}_{model_tag}_{timestamp}_{best_epoch}.pt'
        model_scripted.save(model_path_jitted)  # Save

    return base_dir, model_path, model_path_jitted, model_name


def agressive_train_labeling(epochs, model, optimizer, loss_fn, scheduler, training_loader, validation_loader, report_per_epoch=10,
    writer_base_path="runs", model_base_path=".", model_tag="model", grad_f=None, device="cpu"):
    """
    same as train bug start asynchrone loader more agreessively for more performance
    """

    # Initializing in a separate cell so we can easily add more epochs to the same run
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    writer = SummaryWriter(f"{writer_base_path}/{model_tag}_{timestamp}")

    model_name = f"{model_tag}_{timestamp}"
    base_dir = f"{model_base_path}/{model_name}"
    os.makedirs(base_dir, exist_ok=True)

    n_batch = len(training_loader)

    report_frequency = math.ceil(n_batch / report_per_epoch)

    best_f1_epoch = 0.
    best_f1 = 0.

    best_vloss = 1_000_000.
    best_vloss_epoch = 0

    best_epoch = 0



    model_path = None

    # start the asynchronous loader
    if epochs >0:
        train_iter = iter(training_loader)
        valid_iter = iter(validation_loader)

    with tqdm(total=epochs, desc='Epoch') as pbar:
        for epoch in range(epochs):

            #print('EPOCH {}:'.format(epoch_number + 1))

            # Make sure gradient tracking is on, and do a pass over the data
            model.train(True)
            avg_loss = agressive_train_one_epoch(train_iter, len(training_loader), optimizer, scheduler, model, loss_fn, epoch, writer, report_frequency, grad_f,device)

            if epoch < epochs-1:
                train_iter = iter(training_loader)

            # We don't need gradients on to do reporting
            model.train(True)

            running_vloss = 0.0
            running_vf1 = 0.0
            for i, vdata in enumerate(valid_iter):
                vinputs, vlabels = vdata

                if device is not None:
                    if isinstance(vinputs, (list, tuple)):
                        vinputs = map(lambda x: x.to(device, non_blocking=True), vinputs)
                    else:
                        vinputs = vinputs.to(device, non_blocking=True)  # create a tuple to match with list
                    vlabels = vlabels.to(device, non_blocking=True)

                voutputs = model(*vinputs)
                vloss = loss_fn(voutputs, vlabels)
                running_vloss += vloss.item()

                del vinputs

                vf1 = f1(voutputs.cpu(), vlabels.cpu())
                running_vf1 += vf1
            if epoch < epochs-1:
                valid_iter = iter(validation_loader)

            avg_vloss = running_vloss / (i + 1)
            avg_f1 = running_vf1/ (i + 1)
            #print('LOSS train {} valid {}'.format(avg_loss, avg_vloss))
            #print('Weighted avg f1 {}'.format(avg_f1))

            # Log the running loss averaged per batch
            # for both training and validation
            writer.add_scalars('Training vs. Validation Loss',
                               {'Training': avg_loss, 'Validation': avg_vloss},
                               epoch + 1)
            writer.add_scalars('Weighted avg f1',
                               {'Weighted avg f1': avg_f1},
                               epoch + 1)

            # todo f1 for all v batch at once

            writer.flush()

            # Track the best performance, and save the model's state
            if avg_vloss < best_vloss:
                best_vloss = avg_vloss
                best_vloss_epoch = epoch + 1
                best_epoch = best_vloss_epoch
                best_metric = "loss"
                model_path = f'{base_dir}/{best_metric}_{model_tag}_{timestamp}_{best_vloss_epoch}_{int(1000*best_vloss)}'
                torch.save(model.state_dict(), model_path)

            if avg_f1 > best_f1:
                best_f1 = avg_f1
                best_f1_epoch = epoch+1
                best_epoch = best_f1_epoch
                best_metric = "f1"
                model_path = f'{base_dir}/{best_metric}_{model_tag}_{timestamp}_{best_f1_epoch}_{int(100*best_f1)}'
                torch.save(model.state_dict(), model_path)


            pbar.set_postfix({'best f1 epoch': best_f1_epoch,
                              'best f1': best_f1,
                              'current f1': avg_f1,
                              'best avg loss epoch': best_vloss_epoch,
                              'best avg loss': best_vloss,
                              'current avg loss': avg_vloss}, refresh=False)
            pbar.update(1)


    # load best model
    model.load_state_dict(torch.load(model_path))
    #switch off training
    model.train(False)
    # git model for inference

    vinputs, _ = next(iter(validation_loader))

    if device is not None:
        if isinstance(vinputs, (list, tuple)):
            vinputs = tuple(map(lambda x: x.to(device), vinputs)) #trace need tuple for input
        else:
            vinputs = vinputs.to(device)

    # switch off gradient
    #todo update py torch
    #torch.jit.enable_onednn_fusion(True)
    with torch.inference_mode():
        #model_scripted = torch.jit.script(model, example_inputs=vinputs)  # Export to TorchScript, from the doc: TorchScript is actually the recommended model format for scaled inference and deployment.
        model_scripted = torch.jit.trace(model, example_inputs=vinputs)
        model_scripted = torch.jit.freeze(model_scripted)

        model_path_jitted = f'{base_dir}/jited_{best_metric}_{model_tag}_{timestamp}_{best_epoch}.pt'
        model_scripted.save(model_path_jitted)  # Save

    return base_dir, model_path, model_path_jitted, model_name


def agressive_train_one_epoch(loader_iter, loader_lenght, optimizer, scheduler, model, loss_fn, epoch_index, tb_writer, report_frequency, grad_f=None,
                    device="cpu"):
    """

    :param loader:
    :param optimizer:
    :param model:
    :param loss_fn:
    :param epoch_index:
    :param tb_writer:
    :param report_frequency:
    :param grad_f:
    :param device: device to move tensors to. None for do nothing
    :return:
    """

    running_loss = 0.
    last_loss = 0.
    with tqdm(total=loader_lenght,desc="Batch") as pbar:
        for i, data in enumerate(loader_iter):
            # Every data instance is an input + label pair
            inputs, labels = data

            if device is not None:
                if isinstance(inputs, (list, tuple)):
                    inputs = map(lambda x: x.to(device, non_blocking=True), inputs)
                else:
                    inputs = inputs.to(device, non_blocking=True)

                labels = labels.to(device, non_blocking=True)
            # Zero your gradients for every batch!
            optimizer.zero_grad()

            # Make predictions for this batch
            outputs = model(*inputs)

            # Compute the loss and its gradients
            loss = loss_fn(outputs, labels)
            loss.backward()

            # clip the gradient
            if grad_f is not None:
                grad_f(model)

            # Adjust learning weights
            optimizer.step()
            if scheduler is not None:
                scheduler.step()

            # Gather data and report
            running_loss += loss.item()

            if i % report_frequency == report_frequency - 1:
                pbar.set_postfix({'Batch ': i + 1,
                                  'Last loss': last_loss,
                                  }, refresh=False)
                pbar.update(report_frequency)

                last_loss = running_loss / report_frequency  # loss per item
                #print('  batch {} loss: {}'.format(i + 1, last_loss))
                tb_x = epoch_index * loader_lenght + i + 1
                tb_writer.add_scalar('Loss/train', last_loss, tb_x)
                running_loss = 0.




    return last_loss