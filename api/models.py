from django.db import models


class UserInfo(models.Model):
    user_type_choices=(
        (1,'普通用户'),
        (2,'管理员')
    )
    user_type=models.IntegerField(choices=user_type_choices,verbose_name='用户类型',default=1)
    username=models.CharField(max_length=32,unique=True,verbose_name='用户名')
    password=models.CharField(max_length=64,verbose_name='密码')

    class Meta:
        db_table='UserInfo'
        verbose_name_plural='用户表'

    def __str__(self):
        return self.username


class UserToken(models.Model):
    user=models.OneToOneField(to='UserInfo')
    token=models.CharField(max_length=64,verbose_name='token')


class MachineRoom(models.Model):
    room_name=models.CharField(max_length=32,verbose_name='机房名')

    def __str__(self):
        return self.room_name

    class Meta:
        db_table='MachineRoom'
        verbose_name_plural='机房表'


class PhysicalMachine(models.Model):
    host_active_choices=(
        (0,'无可用资源'),
        (1,'有可用资源')
    )
    machine_name=models.CharField(max_length=64,verbose_name='服务器名',blank=True)
    cpu=models.IntegerField(default=0,verbose_name='CPU核数')
    memory=models.IntegerField(default=0,verbose_name='内存大小/G')
    host_mode=models.CharField(max_length=64,blank=True,verbose_name='主机型号')
    #host_active=models.IntegerField(choices=host_active_choices,default=1,verbose_name='是否可用')
    host_active=models.FloatField(default=0,verbose_name="可用资源\M")
    idrac_ip=models.CharField(max_length=32,blank=True,verbose_name='IDRAC IP')
    host_ip=models.CharField(max_length=32,blank=True,verbose_name='主机IP')
    host_mem_free=models.IntegerField(verbose_name='可用内存/M',default=1)
    create_time=models.DateField(auto_now_add=True)
    update_time=models.DateField(auto_now=True)

    room_site=models.ForeignKey(to='MachineRoom',verbose_name='机房位置')

    def __str__(self):
        return self.machine_name

    class Meta:
        db_table='PhysicalMachine'
        verbose_name_plural='服务器表'
        ordering=['id']


class PhysicalDisk(models.Model):
    disk_name=models.CharField(max_length=32,verbose_name='磁盘名称')
    disk_space=models.IntegerField(default=0,verbose_name='磁盘大小TB')
    disk_free_space=models.FloatField(default=0,verbose_name="可用空间")
    disk_mount=models.ForeignKey(to='PhysicalMachine',verbose_name='挂载宿主机')

    def __str__(self):
        return self.disk_name

    class Meta:
        db_table = 'PhysicalDisk'
        verbose_name_plural='存储表'
        ordering=['id']

# class VmNetName(models.Model):
#     net_adapter = models.CharField(max_length=32,verbose_name="网络适配器")
#     net_mount = models.ManyToManyField("PhysicalMachine")





class VirtualMachine(models.Model):
    vm_audit_choices=(
        (0,'待审核'),
        (1,'审核通过'),
        (2,'审核不通过')
    )
    vm_installed_choices=(
        (0,'未安装'),
        (1,'已安装')
    )
    vm_name=models.CharField(max_length=64,verbose_name='虚拟机名')
    vm_cpu=models.IntegerField(default=0,verbose_name='虚拟机CPU核数')
    vm_memory=models.IntegerField(default=0,verbose_name='虚拟机内存大小')
    vm_os=models.CharField(max_length=64,default='centos7')
    vm_disk=models.IntegerField(verbose_name='磁盘大小GB')
    vm_ip = models.CharField(max_length=32, verbose_name='虚拟机IP')
    vm_gateway = models.CharField(max_length=32, verbose_name='虚拟机网关')
    vm_audit=models.IntegerField(choices=vm_audit_choices,default=0,verbose_name='审核状态')
    vm_installed=models.IntegerField(choices=vm_installed_choices,default=0,verbose_name='是否已安装')
    vm_proposer=models.CharField(max_length=32,verbose_name='申请人')
    vm_createTime=models.DateField(auto_now_add=True)
    vm_updateTime=models.DateField(auto_now=True)
    #增加网卡选项
    vm_netname=models.ForeignKey(to='NetName',default=1)
    host_machine=models.ForeignKey(to='PhysicalMachine')
    vm_datastore=models.ForeignKey(to='PhysicalDisk')
    #vm_net = models.ForeignKey(to='NetName',default=1)

    def __str__(self):
        return self.vm_name

    class Meta:
        db_table='VirtualMachine'
        verbose_name_plural='虚拟机表'
        ordering = ['-id']

class NetName(models.Model):
    name=models.CharField(max_length=32,default='VM Network')