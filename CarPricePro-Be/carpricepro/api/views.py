# api/views.py
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegisterSerializer, UserLoginSerializer, UserSerializer, ChangePasswordSerializer, YourCarModelSerializer
from rest_framework.decorators import action
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from rest_framework import filters
from api.models import Car  # Import mô hình Car từ ứng dụng của bạn
from api.filters import CarFilter
from django_filters.rest_framework import DjangoFilterBackend  # Import DjangoFilterBackend
from rest_framework import generics
from nbconvert import PythonExporter
import nbformat
from django.http import JsonResponse
import pandas as pd
import numpy as np
import locale
from sklearn.metrics import mean_absolute_error
from nbformat import read
import json

class RegisterView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Đăng ký thành công'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        # Đọc dữ liệu từ tệp JSON
        # with open('data.json', 'r', encoding='utf-8') as file:
        #     data = json.load(file)

        # Lặp qua mỗi mục trong danh sách JSON và chèn nó vào cơ sở dữ liệu
        # for item in data:
        #     car = Car(
        #         Model_Xe=item['Model Xe'],
        #         Nam_San_Xuat=item['Năm Sản Xuất'],
        #         Gia_Tien=item['Gía Tiền'],
        #         Xuat_Xu=item['Xuất Xứ'],
        #         Tinh_Trang=item['Tình Trạng'],
        #         Dong_Xe=item['Dòng Xe'],
        #         So_KM_Da_Di=item['Số KM Đã Đi'],
        #         Mau_Ngoai_That=item['Màu Ngoại Thất'],
        #         Mau_Noi_That=item['Màu Nội Thất'],
        #         So_Cho_Ngoi=item['Số Chỗ Ngồi'],
        #         Dong_Co=item['Động Cơ'],
        #         He_Thong_Nap_Nhien_Lieu=item['Hệ Thống Nạp Nhiên Liệu'],
        #         Hop_So=item['Hộp Số'],
        #         Dan_Dong=item['Dẫn Động'],
        #         Thanh_Pho_MPG=item['Thành Phố MPG'],
        #         Cao_Toc_MPG=item['Cao Tốc MPG'],
        #         Chieu_Dai_Co_So=item['Chiều Dài Cơ Sở'],
        #         Chieu_Dai_Xe=item['Chiều Dài Xe'],
        #         Chieu_Rong_Xe=item['Chiều Rộng Xe'],
        #         Chieu_Cao_Xe=item['Chiều Cao Xe'],
        #         Do_Nang=item['Độ Nặng'],
        #         Kich_Thuoc_Dong_Co=item['Kích Thước Động Cơ'],
        #         Ty_So_Duong_Kinh_Xy_Lanh_Pit_Tong=item['Tỷ Số Đường Kính Xy Lanh & Pít Tông'],
        #         Stroke=item['Stroke'],
        #         Ma_Luc=item['Mã Lực'],
        #         So_Vong_Quay_Cuc_Dai=item['Số Vòng Quay Cực Đại'],
        #         Dia_Chi=item['Địa Chỉ']
        #     )
        #     car.save()
            # Lưu mẫu xe vào cơ sở dữ liệu

        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                return Response({'access_token': access_token, 'user': UserSerializer(user).data, 'message': 'Đăng nhập thành công'})
            else:
                return Response({'message': 'Đăng nhập không thành công'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user

            # Kiểm tra nếu người dùng đã đăng nhập (không phải là AnonymousUser)
            if not user.is_anonymous:
                if not user.check_password(serializer.validated_data['old_password']):
                    return Response({'message': 'Mật khẩu cũ không đúng'}, status=status.HTTP_400_BAD_REQUEST)

                user.set_password(serializer.validated_data['new_password'])
                user.save()
                return Response({'message': 'Thay đổi mật khẩu thành công'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Bạn cần đăng nhập để thay đổi mật khẩu'}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
class CarList(generics.ListAPIView):
    queryset = Car.objects.all()
    serializer_class = YourCarModelSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CarFilter

# Funcation send email
def send_question_creation_notification(question_title):
    subject = 'New Question Created'
    message = f"A new question '{question_title}' has been created."
    from_email = 'inssightful-blog@example.com'
    recipient_list = ['admin@gmail.com']  # Thay đổi email admin

    send_mail(subject, message, from_email, recipient_list)

class PredictPriceView(APIView):
    def get(self, request):
        try:
            # Đường dẫn đến tệp .ipynb của bạn
            notebook_path = 'C:/Users/Long/Documents/GitHub/CarPricePro/CarPricePro-Be/carpricepro/api/Car.ipynb'
            print("Đường dẫn tệp Car.ipynb:", notebook_path)

            # Đọc notebook và chuyển đổi thành mã Python
            with open(notebook_path, 'r', encoding='utf-8') as notebook_file:
                notebook_content = read(notebook_file, as_version=4)
                python_exporter = PythonExporter()
                python_code, _ = python_exporter.from_notebook_node(notebook_content)

            # Thực thi mã Python từ notebook
            exec(python_code, globals())

            # Trích xuất tham số từ request.query_params
            input_data = {
                'Chiều Dài Cơ Sở': int(request.query_params.get('chieu_dai_co_so', 0)),
                'Số Chỗ Ngồi': int(request.query_params.get('so_cho_ngoi', 0)),
                'Chiều Dài Xe': int(request.query_params.get('chieu_dai_xe', 0)),
                'Chiều Cao Xe': int(request.query_params.get('chieu_cao_xe', 0)),
                'Hộp Số': int(request.query_params.get('hop_so', 0))
            }
            
            result = predict_price(input_data)

            # Trả về dự đoán giá tiền
            return Response({'predicted_price': result})
        except Exception as e:
            return Response({'error': str(e)})