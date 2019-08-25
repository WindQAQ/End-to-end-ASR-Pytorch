#!/usr/bin/env python
# coding: utf-8
import yaml
import torch
import random
import argparse
import numpy as np

# Make cudnn CTC deterministic
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False

# Arguments
parser = argparse.ArgumentParser(description='Training E2E asr.')
parser.add_argument('--config', type=str, help='Path to experiment config.')
parser.add_argument('--name', default=None, type=str, help='Name for logging.')
parser.add_argument('--logdir', default='log/', type=str, help='Logging path.', required=False)
parser.add_argument('--ckpdir', default='result/', type=str, help='Checkpoint/Result path.', required=False)
parser.add_argument('--load', default=None, type=str, help='Load pre-trained model', required=False)
parser.add_argument('--seed', default=0, type=int, help='Random seed for reproducable results.', required=False)
parser.add_argument('--ctc-backend', default='torch', type=str, help='CTC backend (torch/cudnn)')
parser.add_argument('--njobs', default=1, type=int, help='Number of threads for decoding.', required=False)
parser.add_argument('--cpu', action='store_true', help='Disable GPU training.')
parser.add_argument('--no-pin', action='store_true', help='Disable pin-memory for dataloader')
parser.add_argument('--test', action='store_true', help='Test the model.')
parser.add_argument('--no-msg', action='store_true', help='Hide all messages.')
parser.add_argument('--lm', action='store_true', help='Option for training RNNLM.')
parser.add_argument('--jit', action='store_true', help='Option for enabling jit in pytorch. (feature in development)')
paras = parser.parse_args()
setattr(paras,'gpu',not paras.cpu)
setattr(paras,'pin_memory',not paras.no_pin)
setattr(paras,'verbose',not paras.no_msg)
config = yaml.load(open(paras.config,'r'), Loader=yaml.FullLoader)

random.seed(paras.seed)
np.random.seed(paras.seed)
torch.manual_seed(paras.seed)
if torch.cuda.is_available(): torch.cuda.manual_seed_all(paras.seed)

if paras.lm:
    # Train RNNLM
    from src.solver import LMTrainer as Solver
else:
    if paras.test:
        # Test ASR
        from src.solver import Tester as Solver
    else:
        # Train ASR
        from src.solver import Trainer as Solver
        

solver = Solver(config,paras)
solver.load_data()
solver.set_model()
solver.exec()
