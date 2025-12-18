from abc import ABC

from eoml import torch
from torchmetrics import F1Score


class Score(ABC):

    def __init__(self):
        pass

    def __call__(self):
        pass

    def direction(self):
        pass

    def is_last_best(self):
        pass

    @property
    def best(self):
        return 0

class F1MultiClass(Score):
    def __init__(self, num_class, average="macro", device="cpu"):
        #https://stephenallwright.com/micro-vs-macro-f1-score/
        self._best = float("inf")

        self.score = F1Score(task="multiclass", average=average, num_classes=num_class).to(device)


    def __call__(self, output, target):
        self.score(output, target)

    def direction(self):
        pass

    def is_last_best(self):
        pass

    def best(self):
        return self._best

class F1_Score(ABC):

    def __init__(self):
        pass

    def __call__(self):
        pass

class Trainer:
    """TODO DO AGGRESSIVBE VERSION"""
    def __init__(self, optimizer, model, loss_fn,  grad_f=None, score_function=f1, score_name="f1", score_direction=1):
        self.optimizer = optimizer
        self.model = model
        self.loss_fn = loss_fn
        self.grad_f = grad_f

        self.score_direction = score_direction

        self.writer = None

        self.score_function = score_function
        self.score_name = score_name

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
                    inputs = inputs.to(device, non_blocking=True)
                    labels = labels.to(device, non_blocking=True)
                # Zero your gradients for every batch!
                self.optimizer.zero_grad()

                # Make predictions for this batch
                outputs = self.model(inputs)

                # Compute the loss and its gradients
                loss = self.loss_fn(outputs, labels)
                loss.backward()

                # clip the gradient
                if self.grad_f is not None:
                    self.grad_f(self.model)

                # Adjust learning weights
                self.optimizer.step()

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

    def _validate(self, validation_loader, device):

        self.model.train(False)

        running_vloss = 0.0
        running_score = 0.0

        for i, vdata in enumerate(validation_loader):
            vinputs, vlabels = vdata

            if device is not None:
                vinputs = vinputs.to(device, non_blocking=True)
                vlabels = vlabels.to(device, non_blocking=True)

            voutputs = self.model(vinputs)
            vloss = self.loss_fn(voutputs, vlabels)
            running_vloss += vloss.item()

            vf1 = self.score_function(voutputs.cpu(), vlabels.cpu())
            running_score += vf1

        avg_vloss = running_vloss / (i + 1)
        avg_score = running_score / (i + 1)
        # print('LOSS train {} valid {}'.format(avg_loss, avg_vloss))
        # print('Weighted avg f1 {}'.format(avg_f1))
        return  avg_vloss, avg_score

    def train(self, epochs, training_loader, validation_loader, report_per_epoch=10,
              writer_base_path="runs", model_base_path=".", model_tag="model", device="cpu"):
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

        best_epoch = 0

        model_path = None

        with tqdm(total=epochs, desc='Epoch') as pbar:
            for epoch in range(epochs):

                #print('EPOCH {}:'.format(epoch_number + 1))
                avg_loss = self._epoch(training_loader, epoch, report_frequency, device)

                # We don't need gradients on to do reporting

                avg_vloss, avg_score = self._validate(validation_loader, device)

                # Log the running loss averaged per batch
                # for both training and validation
                self.writer.add_scalars('Training vs. Validation Loss',
                                        {'Training': avg_loss, 'Validation': avg_vloss},
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
                                  'current avg loss': avg_vloss}, refresh=False)
                pbar.update(1)


        # load best model
        self.model.load_state_dict(torch.load(model_path))
        #switch off training
        self.model.train(False)
        # git model for inference

        vinputs, _ = next(iter(validation_loader))

        if device is not None:
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

