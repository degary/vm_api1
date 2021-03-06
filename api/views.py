from django.shortcuts import render
from rest_framework.views import APIView
from api import models
from rest_framework.response import Response
from api.utils.auth import MyAuthentication
from api.utils.auth import md5
from api.utils.headers import get_headers
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet,GenericViewSet
from api.utils.serializer import PhysicalMachineSerializer
from api.utils.serializer import VirtualMachineSerializer
from api.utils.serializer import MachineRoomSerializer
from api.utils.serializer import NetNameSerializer
from api.utils.serializer import PhysicalDiskListSerializer
from  rest_framework.decorators import api_view,authentication_classes
from django_filters.rest_framework import DjangoFilterBackend
import subprocess
import json
from django.http import HttpResponse
from rest_framework import parsers
# Create your views here.

class AuthView(APIView):
    # authentication_classes = [MyAuthentication,]
    def post(self,request,*args,**kwargs):
        ret={'code':1000,'msg':''}
        try:
            user=request.data.get('username')
            pwd=request.data.get('password')
            user_obj=models.UserInfo.objects.filter(username=user,password=pwd).first()
            if not user_obj:
                ret['code']=1001
                ret['msg']='用户名或密码错误'
            else:
                token=md5(user)
                models.UserToken.objects.update_or_create(user=user_obj,defaults={'token':token})
                ret['token']=token
        except Exception as e:
            ret['code']=1002
            ret['msg']='请求异常:%s' % e
        return Response(ret)


class RoomView(ModelViewSet):
    queryset = models.MachineRoom.objects.all().order_by('id')
    serializer_class = MachineRoomSerializer
    pagination_class = PageNumberPagination


class NetView(ModelViewSet):
    queryset = models.NetName.objects.all().order_by('id')
    serializer_class = NetNameSerializer
    pagination_class = PageNumberPagination


class HostView(ModelViewSet):
    # queryset = models.PhysicalMachine.objects.filter(host_active=1).all()
    queryset = models.PhysicalMachine.objects.filter(host_active__gte=0).all()
    serializer_class = PhysicalMachineSerializer
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('host_ip',)

    def headers(self,request,*args,**kwargs):
        header_fields_list = models.PhysicalMachine._meta.fields
        header_dic=get_headers(header_fields_list)
        return Response(header_dic)


class DiskView(ModelViewSet):
    # queryset = models.PhysicalMachine.objects.filter(host_active=1).all()
    queryset = models.PhysicalDisk.objects.all()
    serializer_class = PhysicalMachineSerializer
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('host_ip',)

    def headers(self,request,*args,**kwargs):
        header_fields_list = models.PhysicalDisk._meta.fields
        header_dic=get_headers(header_fields_list)
        return Response(header_dic)



class VHostView(ModelViewSet):
    queryset = models.VirtualMachine.objects.all().select_related()
    serializer_class = VirtualMachineSerializer
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filter_fields=('vm_installed','vm_audit')

    def headers(self,request,*args,**kwargs):
        header_fields_list = models.VirtualMachine._meta.fields
        header_dic=get_headers(header_fields_list)
        # print(header_fields_list)
        # print(header_dic)
        return Response(header_dic)

    # authentication_classes = ['MyAuthentication',]
    # @api_view(['update'])
    # @authentication_classes((MyAuthentication,))
    # def update(self, request, *args, **kwargs):
    #     pass


class VHostCreate(APIView):
    def get(self,request,*args,**kwargs):
        ret = {'code': 2000, 'msg': ''}
        create='/usr/bin/python3 /export/VMWare_Auto/vm_create/bin/create_if_vm.py'
        obj = subprocess.Popen(create, shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        stdout = obj.stdout.read()
        stderr = obj.stderr.read()
        if stderr:
            ret["err"] = stderr.decode('utf-8')
            ret["code"] = 2001
        else:
            ret["msg"] = '虚拟机安装中'
        return Response(ret)


class VDisconnect(APIView):
    def get(self,request,*args,**kwargs):
        ret={'code': 2100, 'msg': ''}
        ip=request.query_params.get('ip')
        obj=models.VirtualMachine.objects.filter(vm_ip=ip).first()
        if obj:
            vm_name=obj.vm_name
            dc=obj.host_machine.room_site.room_name
            # print(vm_name,dc)
            disconnect='python3 "D:\\myproject\\vm_create\\bin\\discdrom.py" "%s" "%s"'%(dc,vm_name)
            obj = subprocess.Popen(disconnect, shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
            stdout = obj.stdout.read()
            stderr = obj.stderr.read()
            if stderr:
                ret["msg"] = stderr.decode('utf-8')
                ret["code"] = 2101
            else:
                ret["msg"] = 'cdrom已断开'
        return Response(ret)

class GetMemInfo(APIView):
    def get(self,request,*args,**kwargs):
        ret = {'code': 2200, 'msg': ''}
        host_ip = request.query_params.get('host_ip')
        get_info='python3 /opt/app/vm_create/bin/gethostinfo.py %s' %(host_ip)
        obj = subprocess.Popen(get_info, shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        stdout=obj.stdout.read()
        stderr=obj.stderr.read()
        if stdout:
            res = {}
            res["Mem_free"] = str(stdout.strip())
            json.dumps(res)
            if stderr:
                ret["msg"] = stderr.decode('utf-8')
                ret["code"] = 2222
            else:
                return HttpResponse(res)

class DiskListView(ModelViewSet):
    queryset = models.PhysicalDisk.objects.all().order_by('id')
    serializer_class = PhysicalDiskListSerializer
    pagination_class = PageNumberPagination
    # filter_fields = ('id',)

    def headers(self,request,*args,**kwargs):
        header_fields_list = models.PhysicalDisk._meta.fields
        header_dic=get_headers(header_fields_list)
        # print(header_fields_list)
        # print(header_dic)
        return Response(header_dic)






