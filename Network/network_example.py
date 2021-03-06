import tensorflow as tf
import Transform_Data as td
import numpy as np

#跟踪Validation最大值
max_accuracy=0
#Early Stop的计数器，到10就中止训练
timer=0
#定义的Confusion Matrix,初始值是7*7的0矩阵
confusion_matrics=np.zeros([7,7],dtype="int")
#学习率初始值1e-4
learning_rate=1e-4

#三个集合的batch大小
training_batch_size=100
validation_batch_size=40
test_batch_size=40

#Epoch数
Epoch=300

len_training_data, validation, test = td.Initialization(validation_batch_size,test_batch_size)
#将所有训练数全部送入神经网络训练一个周期的迭代次数
iteration_time=int(len_training_data/training_batch_size)+1

#设置会话
sess=tf.InteractiveSession()

#权重初始化
def weight_variable(shape):
    initial = tf.truncated_normal(shape, stddev=0.1)
    return tf.Variable(initial)
#偏置初始化
def bias_variable(shape):
    initial=tf.constant(0.1, shape=shape)
    return tf.Variable(initial)
#2D卷积运算
def conv2d(x,w):
    return tf.nn.conv2d(x, w, strides=[1, 1, 1, 1], padding='SAME')
#Max-Pooling运算
def max_pool_2x2(x):
    return tf.nn.max_pool(x, ksize=[1, 2, 2, 1],strides=[1, 2, 2, 1],padding='SAME')
#Average-Pooling运算
def avg_pool_2x2(x):
    return tf.nn.avg_pool(x, ksize=[1,2,2,1], strides=[1,2,2,1], padding='SAME')

#########################################网络部分##########################################
#输入层，输入图像x和标签y_
#name_scope是Tensorboard构图用语，用于标明在Tensorboard中结点的名称，节点名称可以存在嵌套关系
with tf.name_scope('Input'):
    with tf.name_scope('Input_x'):
        x = tf.placeholder(tf.float32,shape=[None,1024])
    with tf.name_scope('Input_y'):
        y_ = tf.placeholder(tf.float32,shape=[None,7])

with tf.name_scope('Conv_1'):
    with tf.name_scope('W_conv1'):
        #3*3卷积核，输入通道1，输出通道8
        w_conv1=weight_variable([3,3,1,8])
    with tf.name_scope('B_conv1'):
        b_conv1=bias_variable([8])
    with tf.name_scope('x_image'):
        #将输入的数据转成32*32大小的1通道数据
        x_image=tf.reshape(x,[-1,32,32,1])
    with tf.name_scope('H_conv1'):
        #Sigmoid激活函数
        h_conv1=tf.nn.sigmoid(conv2d(x_image,w_conv1)+b_conv1)

with tf.name_scope('Conv_2'):
    with tf.name_scope('W_conv2'):
        #3*3卷积核，输入通道8，输出通道16
        w_conv2=weight_variable([3,3,8,16])
    with tf.name_scope('B_conv2'):
        b_conv2=bias_variable([16])
    with tf.name_scope('H_conv2'):
        #Sigmoid激活函数
        h_conv2=tf.nn.sigmoid(conv2d(h_conv1,w_conv2)+b_conv2)
    with tf.name_scope('H_pool2'):
        #作一次Max-Pooling
        h_pool2=max_pool_2x2(h_conv2)

with tf.name_scope('Conv_3'):
    with tf.name_scope('W_conv3'):
        #3*3卷积核，输入通道16，输出通道32
        w_conv3=weight_variable([3,3,16,32])
    with tf.name_scope('B_conv3'):
        b_conv3=bias_variable([32])
    with tf.name_scope('H_conv3'):
        #Sigmoid激活函数
        h_conv3=tf.nn.sigmoid(conv2d(h_pool2,w_conv3)+b_conv3)

with tf.name_scope('Conv_4'):
    with tf.name_scope('W_conv4'):
        #3*3卷积核，输入通道32，输出通道64
        w_conv4=weight_variable([3,3,32,64])
    with tf.name_scope('B_conv4'):
        b_conv4=bias_variable([64])
    with tf.name_scope('H_conv4'):
        #Sigmoid激活函数
        h_conv4=tf.nn.sigmoid(conv2d(h_conv3,w_conv4)+b_conv4)
    with tf.name_scope('H_pool4'):
        #作一次Max-Pooling
        h_pool4=max_pool_2x2(h_conv4)

with tf.name_scope('Conv_5'):
    with tf.name_scope('W_conv5'):
        #3*3卷积核，输入通道64，输出通道128
        w_conv5=weight_variable([3,3,64,128])
    with tf.name_scope('B_conv5'):
        b_conv5=bias_variable([128])
    with tf.name_scope('H_conv5'):
        #Sigmoid激活函数
        h_conv5=tf.nn.sigmoid(conv2d(h_pool4,w_conv5)+b_conv5)

with tf.name_scope('Conv_6'):
    with tf.name_scope('W_conv6'):
        #3*3卷积核，输入通道128，输出通道256
        w_conv6=weight_variable([3,3,128,256])
    with tf.name_scope('B_conv6'):
        b_conv6=bias_variable([256])
    with tf.name_scope('H_conv6'):
        #Sigmoid激活函数
        h_conv6=tf.nn.sigmoid(conv2d(h_conv5,w_conv6)+b_conv6)
    with tf.name_scope('H_pool6'):
        #作一次Max-Pooling
        h_pool6=max_pool_2x2(h_conv6)

with tf.name_scope('Full_Connected_Layer_1'):
    with tf.name_scope('W_fc1'):
        #三次Max-Pooling后，32*32变成4*4，Feature map为256，连接一个1024神经元的全连接层
        w_fc1=weight_variable([4*4*256,1024])
    with tf.name_scope('B_fc1'):
        b_fc1=bias_variable([1024])
    with tf.name_scope('H_pool_flat'):
        #将第六个卷积层输出结果转成4*4*256一维向量
        h_pool_flat=tf.reshape(h_pool6,[-1,4*4*256])
    with tf.name_scope('H_fc1'):
        #Relu激活函数
        h_fc1=tf.nn.relu(tf.matmul(h_pool_flat,w_fc1)+b_fc1)

with tf.name_scope('Full_Connected_Layer_2'):
    with tf.name_scope('W_fc2'):
        #1024个神经元连接7个神经元，做分类
        w_fc2=weight_variable([1024,7])
    with tf.name_scope('B_fc2'):
        b_fc2=bias_variable([7])
    with tf.name_scope('Y_conv'):
        #Softmax做分类
        y_conv=tf.nn.softmax(tf.matmul(h_fc1,w_fc2)+b_fc2)
#################################网络部分结束#############################################

#########################定义loss function，Accuracy计算方式等定义########################
with tf.name_scope('Cross_Entropy'):
    #loss function为交叉熵，y_conv截断至1e-10到1.0
    cross_entropy = -tf.reduce_sum(y_ * tf.log(tf.clip_by_value(y_conv, 1e-10, 1.0)))
    #Tensorboard的变量监测
    tf.summary.scalar('Cross_Entropy',cross_entropy)
with tf.name_scope('Train_Step'):
    #用Adam优化器优化交叉熵，学习率默认1e-4
    train_step=tf.train.AdamOptimizer(learning_rate).minimize(cross_entropy)
with tf.name_scope('Correct_prediction'):
    #统计y_和y_conv在第一维度的数值
    distribution=[tf.arg_max(y_,1),tf.arg_max(y_conv,1)]
    #判断y_和y_conv相等的情况，输出一系列布尔值
    correct_prediction=tf.equal(distribution[0],distribution[1])
with tf.name_scope('Accuracy'):
    #将correct_prediction转成float型，计算correct_prediction的平均值。
    accuracy=tf.reduce_mean(tf.cast(correct_prediction,"float"))
    #变量监测
    tf.summary.scalar('Accuracy',accuracy)

#汇总所有Tensorboard的监测项
merged=tf.summary.merge_all()
#Tensorboard的生成文件路径
writer=tf.summary.FileWriter('D:/Log',sess.graph)
#周期数
epoch=0

#################################各种定义结束############################################

##################################网络训练开始###########################################
saver=tf.train.Saver()
First_training=True
checkpoint_epoch=10
checkpoint_dir='D:\\Checkpoint\\model.ckpt'

if First_training==False:
    ckpt=tf.train.get_checkpoint_state(checkpoint_dir)
    if ckpt and ckpt.model_checkpoint_path:
        saver.restore(sess,checkpoint_dir)
    else:pass

#初始化所有变量
sess.run(tf.global_variables_initializer())

for i in range(Epoch*iteration_time+1):
    #Batch Size
    batch = td.next_batch(training_batch_size)
    #开始训练，batch[0]是n个image,batch[1]是n个label
    train_step.run(feed_dict={x: batch[0], y_: batch[1]})
    #当迭代次数达到一个Epoch时：
    if i % (iteration_time) == 0 and i != 0:
        epoch += 1
        #计算训练集准确率
        train_accuracy=accuracy.eval(feed_dict={x: batch[0], y_: batch[1]})
        #计算验证集准确率
        validation_accuracy_resultSet = []
        for j in range(len(validation)):
            validation_accuracy = accuracy.eval(feed_dict={x: validation[j][0], y_: validation[j][1]})
            validation_accuracy_resultSet.append(validation_accuracy)
        validation_accuracy = np.sum(validation_accuracy_resultSet) / len(validation_accuracy_resultSet)
        #动态调整学习率
        if validation_accuracy<0.8:
            learning_rate=1e-4
        if validation_accuracy>=0.8:
            learning_rate=5e-5
        if validation_accuracy>=0.9:
            learning_rate=1e-5
        print("Epoch %d , training accuracy %g,Validation Accuracy: %g" % (epoch, train_accuracy, validation_accuracy))
        print(sess.run(cross_entropy,feed_dict={x:batch[0],y_:batch[1]}))
        #每一个周期把信息写入Tensorboard
        result = sess.run(merged, feed_dict={x: batch[0], y_: batch[1]})
        writer.add_summary(result, epoch)
        saver.save(sess,checkpoint_dir,global_step=epoch)
        #Early Stop方法
        if validation_accuracy>max_accuracy:
            max_accuracy=validation_accuracy
            timer=0
        else:
            timer+=1
            if timer>15:   #原来是10
                break
#####################################训练结束############################################

#训练完毕后，计算测试集上的识别率,方法与Validation Data类似
test_accuracy_resultSet=[]
for j in range(len(test)):
    matrix_row, matrix_col = sess.run(distribution, feed_dict={x: test[j][0], y_: test[j][1]})
    for m, n in zip(matrix_row, matrix_col):
        confusion_matrics[m][n] += 1
    test_accuracy = accuracy.eval(feed_dict={x: test[j][0], y_: test[j][1]})
    test_accuracy_resultSet.append(test_accuracy)
test_accuracy = np.sum(test_accuracy_resultSet) / len(test_accuracy_resultSet)

print("Test Accuracy :",test_accuracy)
print(np.array(confusion_matrics.tolist()))