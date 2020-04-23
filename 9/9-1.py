# GAN default model

import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt

from tensorflow.examples.tutorials.mnist import input_data
mnist = input_data.read_data_sets("./mnist/", one_hot=True)

total_epoch = 100
batch_size = 100
learning_rate = 0.0002
n_hidden = 256
n_input = 28 * 28
n_noise = 128

X = tf.placeholder(tf.float32, [None, n_input])
Z = tf.placeholder(tf.float32, [None, n_noise])

# 생성자 신경망 변수
# 노이즈 - 은닉층 - 출력
G_W1 = tf.Variable(tf.random_normal([n_noise, n_hidden], stddev=0.01))
G_b1 = tf.Variable(tf.zeros([n_hidden]))
G_W2 = tf.Variable(tf.random_normal([n_hidden, n_input], stddev=0.01))
G_b2 = tf.Variable(tf.zeros([n_input]))

# 구분자 신경망 변수
# 입력층 - 은닉층 - 0~1 사이의 결과값
D_W1 = tf.Variable(tf.random_normal([n_input, n_hidden], stddev=0.01))
D_b1 = tf.Variable(tf.zeros([n_hidden]))
D_W2 = tf.Variable(tf.random_normal([n_hidden, 1], stddev=0.01))
D_b2 = tf.Variable(tf.zeros([1]))

# 생성자 신경망 noise_z = [batchsize , noise] = [100,128]
def generator(noise_z):
    hidden = tf.nn.relu(tf.matmul(noise_z, G_W1) + G_b1)
    output = tf.nn.sigmoid(tf.matmul(hidden, G_W2) + G_b2)

    return output

# 구분자 신경망
def discriminator(inputs):
    hidden = tf.nn.relu(tf.matmul(inputs, D_W1) + D_b1)
    output = tf.nn.sigmoid(tf.matmul(hidden, D_W2) + D_b2)

    return output

# 무작위 노이즈 생성 유틸리티
def get_noise(batch_size, n_noise):
    return np.random.normal(size=(batch_size, n_noise))

G = generator(Z)
D_gene = discriminator(G)
D_real = discriminator(X)

loss_D = tf.reduce_mean(tf.log(D_real) + tf.log(1-D_gene))
loss_G = tf.reduce_mean(tf.log(D_gene))

D_var_list = [D_W1, D_b1, D_W2, D_b2]
G_var_list = [G_W1, G_b1, G_W2, G_b2]

train_D = tf.train.AdamOptimizer(learning_rate).minimize(-loss_D, var_list=D_var_list)
train_G = tf.train.AdamOptimizer(learning_rate).minimize(-loss_G, var_list=G_var_list)

# 무작위 노이즈를 무작위 숫자로 변경해주는 신경망인가요?!
with tf.Session() as sess:
    init = tf.global_variables_initializer()
    sess.run(init)

    total_batch = int(mnist.train.num_examples / batch_size)
    loss_val_D, loss_val_G = 0, 0

    for epoch in range(total_epoch):
        for i in range(total_batch):
            # mnist 데이터에서 batch_size 만큼의 이미지를 가져옴
            batch_xs, batch_ys = mnist.train.next_batch(batch_size)
            # [100,128]의 무작위 행렬 생성 생성
            noise = get_noise(batch_size, n_noise)

            # train_D - 구분자 학습
            # D_real = discriminator(X) - input 형태의 실제 batch_xs들을 구분자 신경망을 통과시킴
            # 노이즈 또한 구분자 신경망을 통과시킴
            # 실제 일치율 + 노이지 이미지 가능성이가 최대가 신경망을 학습시킴
            _,loss_val_D = sess.run([train_D, loss_D], feed_dict={X:batch_xs, Z:noise})

            # train_G - 생성자 학습
            # -loss_G가 최소가 되도록 G_var_list 함수들을 실행
            # train_G 
            # G = generator(Z) - Z =랜덤한 - input 형태로 랜덤가공을 진행
            # D_gene = discriminator(G) - input 형태의 noise 를 구분자 신경망을 통과시킴
            # 일치율이 최대가 되도록 신경망을 학습
            _,loss_val_G = sess.run([train_G, loss_G], feed_dict={Z:noise})

        print('Epoch:', '%04d' % epoch, 'D loss: {:.4}'.format(loss_val_D), 'G loss: {:.4}'.format(loss_val_G))

        if epoch == 0 or (epoch + 1) % 10 == 0:
            sample_size = 10
            noise = get_noise(sample_size, n_noise)
            samples = sess.run(G, feed_dict={Z:noise})

            fig, ax = plt.subplots(1, sample_size, figsize=(sample_size, 1))

            for i in range(sample_size):
                ax[i].set_axis_off()
                ax[i].imshow(np.reshape(samples[i], (28,28)))

            plt.savefig('samples/{}.png'.format(str(epoch).zfill(3)), bbox_inches='tight')

            plt.close(fig)
        print('최적화 완료')