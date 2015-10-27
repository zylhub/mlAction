#/usr/bin/env python
from theano.tensor.shared_randomstreams import RandomStreams
import theano.tensor as T
import theano
import numpy
import timeit
import os
import sys
from PIL import Image

class dA(object):
    """docstring for dA"""
    def __init__(self, 
                numpy_rng, 
                theano_rng=None, 
                input=None, 
                n_visible=784, 
                n_hidden=500,
                W=None,
                bhid=None,
                bvis=None):
        # super(dA, self).__init__()
        self.n_visible = n_visible
        self.n_hidden = n_hidden
        if not theano_rng:
            theano_rng = RandomStreams(numpy_rng.randint(2**30))

        if not W:
            initial_W = numpy.asarray(
                numpy_rng.uniform(
                    low=-4*numpy.sqrt(6./(n_hidden + n_visible)),
                    high=4*numpy.sqrt(6./(n_hidden + n_visible)),
                    size=(n_hidden + n_visible)
                ),
                dtype=theano.config.floatX
            )
            W = theano.shared(value=initial_W, name='W', borrow=True)

        if not bvis:
            bvis = theano.shared(
                value=numpy.zeros(
                    n_visible,
                    dtype=theano.config.floatX
                    ),
                borrow=True
            )

        if not bhid:
            bhid = theano.shared(
                value=numpy.zeros(
                    n_hidden,
                    dtype=theano.config.floatX
                    ),
                name='W',
                borrow=True
            )

        self.W = W
        self.b = bhid
        self.b_prime = bvis
        self.W_prime = self.W.T
        self.theano_rng = theano_rng
        if input is None:
            self.x = T.matrix(name='input')
        else:
            self.x = input
        self.params = [self.W, self.b, self.b_prime]
        def get_cost_updates(self, corruption_level, learning_rate):
            tildex_x = self.get_corrupted_input(self.x, corruption_level)
            y = self.get_hidden_values(tildex_x)
            z = self.get_reconstructed_input(y)
            L = -T.sum(self.x * T.log(z) + (1 - self.x) * T.log(1-z), axis=1)
            cost = T.mean(L)
            gparams = T.grad(cost, self.params)
            updates = [
                (param, param - learning_rate*gparam)
                for param,gparam in zip(self.params, gparams)
            ]
            return (cost, updates)
        def get_hidden_values(self, input):
            return T.nnet.sigmoid(T.dot(input, self.W) + self.b)
        def get_reconstructed_input(self, hidden):
            return T.nnet.sigmoid(T.dot(hidden, self.W_prime) + self.b_prime)
        def get_corrupted_input(self, input, corruption_level):
            return self.theano_rng.binomial(size=input.shape, n=1, p=1-corruption_level)*input


# def test_dA(learning_rate=0.1, training_epochs=15, 
#             dataset='mnist.pkl.gz', batch_size=20, 
#             output_folder='dA_plots'):
index = T.lscalar()
x = T.matrix('x')
# rng = numpy.random.RandomState(123)
# theano_rng = RandomStreams(rng.randint(2**30))

# da  = dA(
#     numpy_rng=rng,
#     theano_rng=theano_rng,
#     input=x,
#     n_visible=28*28,
#     n_hidden=500
# )
# cost,updates = da.get_cost_updates(
#     corruption_level=0.,
#     learning_rate=learning_rate
# )
# train_da = theano.function(
#     [index],
#     cost,
#     updates=updates,
#     givens={
#         x:train_set_x[index*batch_size: (index+1)*batch_size]
#         }
# )
# start_time = timeit.default_timer()
# for epoch in xrange(training_epochs):
#     c = []
#     for batch_index in xrange(n_train_batches):
#         c.append(train_da(batch_index))
#     print 'Training epoch %d, cost '%epoch,numpy.mean(c)
# end_time = timeit.default_timer()
# training_time = (end_time - start_time)
# print >> sys.stderr, ('The no corruption code for file ' + os.path.split(__file__)[1] +
#             'ran for %.2fm'%((training_time)/60.))

# image = Image.fromarray(
#     tile_raster_images(X=da.W.get_value(borrow=True).T,
#                         ima_shape=(28*28), tile_shape=(10,10),
#                         title_spacing=(1,1)))    
# image.save('filters_corruption_0.png')
rng = numpy.random.RandomState(123)
theano_rng = RandomStreams(rng.randint(2**30))
da = dA(
    numpy_rng=rng,
    theano_rng=theano_rng,
    input=x,
    n_visible=28*28,
    n_hidden=500
)

cost, updates = da.get_cost_updates(
    corruption_level=0.3,
    learning_rate=learning_rate
)

train_da = theano.function(
    [index],
    cost,
    updates=updates,
    givens={
        x: train_set_x[index * batch_size: (index + 1) * batch_size]
    }
)

start_time = timeit.default_timer()

############
# TRAINING #
############

# go through training epochs
for epoch in xrange(training_epochs):
    # go through trainng set
    c = []
    for batch_index in xrange(n_train_batches):
        c.append(train_da(batch_index))

    print 'Training epoch %d, cost ' % epoch, numpy.mean(c)

end_time = timeit.default_timer()

training_time = (end_time - start_time)

print >> sys.stderr, ('The 30% corruption code for file ' +
                      os.path.split(__file__)[1] +
                      ' ran for %.2fm' % (training_time / 60.))


