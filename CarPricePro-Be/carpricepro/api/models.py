# api/models.py
import django_filters
from django.db import models
from django.contrib.auth.models import User

class Car(models.Model):
    Model_Xe = models.CharField(max_length=255)
    Nam_San_Xuat = models.IntegerField()
    Gia_Tien = models.DecimalField(max_digits=15, decimal_places=2)
    Xuat_Xu = models.CharField(max_length=255)
    Tinh_Trang = models.IntegerField()
    Dong_Xe = models.CharField(max_length=255)
    So_KM_Da_Di = models.IntegerField()
    Mau_Ngoai_That = models.CharField(max_length=255)
    Mau_Noi_That = models.CharField(max_length=255)
    So_Cho_Ngoi = models.IntegerField()
    Dong_Co = models.CharField(max_length=255)
    He_Thong_Nap_Nhien_Lieu = models.CharField(max_length=255)
    Hop_So = models.CharField(max_length=255)
    Dan_Dong = models.CharField(max_length=255)
    Thanh_Pho_MPG = models.IntegerField()
    Cao_Toc_MPG = models.IntegerField()
    Chieu_Dai_Co_So = models.DecimalField(max_digits=5, decimal_places=1)
    Chieu_Dai_Xe = models.DecimalField(max_digits=5, decimal_places=1)
    Chieu_Rong_Xe = models.DecimalField(max_digits=5, decimal_places=1)
    Chieu_Cao_Xe = models.DecimalField(max_digits=5, decimal_places=1)
    Do_Nang = models.IntegerField()
    Kich_Thuoc_Dong_Co = models.DecimalField(max_digits=4, decimal_places=1)
    Ty_So_Duong_Kinh_Xy_Lanh_Pit_Tong = models.DecimalField(max_digits=3, decimal_places=2)
    Stroke = models.DecimalField(max_digits=3, decimal_places=2)
    Ma_Luc = models.IntegerField()
    So_Vong_Quay_Cuc_Dai = models.IntegerField()
    Dia_Chi = models.CharField(max_length=255)

    def __str__(self):
        return self.Model_Xe
    