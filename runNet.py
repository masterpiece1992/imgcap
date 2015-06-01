### NOTE: IF YOU ARE NOT USING IPYTHON, REMOVE THE NEXT TWO LINES
#%load_ext autoreload
#%autoreload 2

import numpy as np
from tlstm.datahandler import DataHandler
from datetime import datetime
import optparse
import cPickle as pickle
import conf as opts
import shutil
from tlstm.tlstm import TLSTM
from tlstm.twin import Twin
from tlstm import sgd as optimizer
import os

# ensure the options are valid
assert opts.megabatch_size % opts.minibatch_size == 0
assert type(opts.data_type) == str
opts.data_type = opts.data_type.lower()
assert opts.data_type in ['vgg16','vgg19','both']

test_mode = True

# set opts that have only one possible value
opts.numWords = 33540
opts.imageDim = 4096
if opts.data_type == 'both':
    opts.imageDim *= 2

# instantiate the data handler
dh = DataHandler(opts.root, opts.megabatch_size, opts.minibatch_size, opts.val_size, opts.test_size, opts.data_type, opts.epoch_lim)

dh.cur_iteration = 0

if opts.saved_model is not None:
	params = np.load(opts.saved_model)
else:
	params = None


# instantiate the second 'layer'
net2 = Twin(opts.sentenceDim, opts.imageDim, opts.sharedDim, opts.numLayers, 1./(opts.mbSize*(opts.mbSize-1)), opts.reg, params=params)
#net2 = Twin(opts.sentenceDim, opts.imageDim, opts.sharedDim, opts.numLayers, 1./(opts.mbSize*(opts.mbSize-1)), 0)

# instantiate the first 'layer'
net1 = TLSTM(opts.wvecDim, opts.middleDim, opts.paramDim, opts.numWords, opts.mbSize, 1./(opts.mbSize*(opts.mbSize-1)), opts.rho, net2, root=opts.root, params=params)

#net1 = TLSTM(opts.wvecDim, opts.middleDim, opts.paramDim, opts.numWords, opts.mbSize, 1./(opts.mbSize*(opts.mbSize-1)), 0, net2)

# instantiate the SGD
pfxm = "models/m_%s"%datetime.now().strftime("%m%d_%H%M%S")
try:
    os.mkdir(pfxm)
except Exception, e:
    pass
pfxL = "logs/m_%s"%datetime.now().strftime("%m%d_%H%M%S")
try:
    os.mkdir(pfxL)
except Exception, e:
    pass

model_filename = os.path.join(pfxm, 'megabatch_%s')
log_filename = os.path.join(pfxL, 'megabatch_%s')
shutil.copyfile("conf.py", os.path.join(pfxm, 'config'))

sgd = optimizer.SGD(net1, model_filename, opts.alpha, dh, optimizer=opts.optimizer, logfile=log_filename, test_inc=opts.test_inc)

#sgd = optimizer.SGD(net1, 1e-5, dh, optimizer='sgd')

sgd.run()
sgd.save_checkpoint("final")
