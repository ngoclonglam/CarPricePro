import requests
import time
import csv
import re
import random
import json
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator

# Function for change the money type to our style - using for VND format with char (triệu, tỷ)
def custom_translate(text, translation):
    regex = re.compile('|'.join(map(re.escape, translation)))
    return regex.sub(lambda match: translation[match.group(0)], text)

# Function to remove \t \n from the string
def remove_t_n(char):
    n = {
            '\t' : None,
            '\n' : '',
        }
    x = str.maketrans(n)
    char = char.translate(x)
    
# Function to transfer dollar to VND
def currency_change(money):
    change = money.split(',')
    price = ''.join(change)
    return int(price) * 23000
    
# Function to convert mile to km
def convert_to_kmh(miles):
    convert_mile = miles.replace('.', '')
    if int(convert_mile) < 1000:
        return round((float(miles) * 1.6), 3) # Convert
    return '{:.3f}'.format(float(miles) * 1.6)
    
# Debug function for car seats
def car_seats(car_type):
    match car_type:
        case 'coupe':
            return '2'
        case 'van-minivan':
            return str(random.randint(5, 7))
        case 'sedan':
            return str(random.randint(4, 5))
        case 'truck':
            return str(random.randint(2, 6))
        case 'wagon':
            return '5'
        case 'hatchback':
            return str(random.randint(4, 5))
        case 'suv-crossover':
            return str(random.randint(5, 7))
        case 'convertible':
            return '4'
        case default:
            return 'Unknown'
    
# Default header for owner's website know who we are
headers = {
    'User-Agent': 'TDTU STUDENT (Viet Nam)',
    'From': 'ngoclonglam@yahoo.com.vn',
}

url = 'https://autotrader.com/cars-for-sale/used-cars'
page = requests.get(url, headers = headers)

# Write the base column for csv file
f = csv.writer(open('autotrader.csv', 'w', encoding = 'utf-16'))
f.writerow(['Model Xe', 'Năm Sản Xuất', 'Gía Tiền', 'Xuất Xứ', 'Tình Trạng', 'Dòng Xe', 'Số KM Đã Đi', 'Màu Ngoại Thất', 'Màu Nội Thất', 
            'Số Chỗ Ngồi', 'Động Cơ', 'Hệ Thống Nạp Nhiên Liệu', 'Hộp Số', 'Dẫn Động', 'Thành Phố MPG', 'Cao Tốc MPG', 
            'Chiều Dài Cơ Sở', 'Chiều Dài Xe', 'Chiều Rộng Xe', 'Chiều Cao Xe', 'Độ Nặng', 'Kích Thước Động Cơ', 
            'Tỷ Số Đường Kính Xy Lanh & Pít Tông', 'Stroke', 'Mã Lực', 'Số Vòng Quay Cực Đại', 'Địa Chỉ'])

# Init storage
models       = []
years        = []
prices       = []
origin       = []
status       = []
type_car     = []
drive_km     = []
color_out    = []
color_in     = []
seats        = []
engine       = []
gear         = []
fuel_system  = []
drive_shaft  = []
citys        = []
highways     = []
wheelbases   = []
carlengths   = []
carwidths    = []
carheights   = []
curbweights  = []
enginesizes  = []
boreratios   = []
strokes      = []
horsepowers  = []
peakrpm      = []
addresses    = []


# Link storage
pages      = []
links      = []
car_link   = []
body_style = ['van-minivan', 'coupe', 'sedan', 'truck', 'wagon', 'hatchback', 'suv-crossover', 'convertible']
# body_style = ['coupe']

# Google Translator
gg_trans = GoogleTranslator(source = 'auto', target = 'vi')

# Some variables for debug
flag_in  = False
flag_out = False

# Some list for process
engine_a  = []
engine_b  = []
list_type = []
ignore_w  = [
             'http://autotrader.com//cars-for-sale/vehicledetails.xhtml?listingId=689833759&firstRecord=48&isNewSearch=false&listingTypes=USED&referrer=%2Fcars-for-sale%2Ftruck%3FfirstRecord%3D48&vehicleStyleCodes=TRUCKS&clickType=listing',
             'http://autotrader.com//cars-for-sale/vehicledetails.xhtml?listingId=689283569&firstRecord=0&isNewSearch=false&listingTypes=USED&',
             'http://autotrader.com//cars-for-sale/vehicledetails.xhtml?listingId=676819064&firstRecord=0&isNewSearch=false&listingTypes=USED&referrer=%2Fcars-for-sale%2Fwagon%3FfirstRecord%3D0&vehicleStyleCodes=WAGON&clickType=listing',
             'http://autotrader.com//cars-for-sale/vehicledetails.xhtml?listingId=690340572&firstRecord=24&isNewSearch=false&listingTypes=USED&referrer=%2Fcars-for-sale%2Fconvertible%3FfirstRecord%3D24&vehicleStyleCodes=CONVERT&clickType=listing',
             'http://autotrader.com//cars-for-sale/vehicledetails.xhtml?listingId=690192132&firstRecord=24&isNewSearch=false&listingTypes=USED&referrer=%2Fcars-for-sale%2Fcoupe%3FfirstRecord%3D24&vehicleStyleCodes=COUPE&clickType=listing'
            ]

# Some string sample for check 
auto_trans = 'Automatic Transmission'
exterior   = 'Exterior'
interior   = 'Interior'
awd        = 'All wheel drive'
rfd        = '2 wheel drive - rear'
fwd        = '2 wheel drive - front'
city       = 'City'
highway    = 'Highway'

# ramdon choice in list body_style
# print(random.choice(body_style))

for i in range(0, 10):
    # Get the car link on auto trader with parameter firstRecord += 24 for each page
    for j in body_style:
        url = 'https://autotrader.com/cars-for-sale/' + j + '?firstRecord=' + str(i * 24)
        pages.append(url)
        # list_type.append(j)
        print('Check type_car: ', j)
    
for item in pages:
    # Get context of HTML source from the link
    page = requests.get(item)
    soup = BeautifulSoup(page.text, 'lxml')
    
    # Get the href attrs to access car details
    car_links = soup.select('div.positioned-overlay-base.image-container')
    links = [link.find('a').attrs['href'] for link in car_links]
    
    for link in links:
        # Append new URL into links
        url_link = 'http://autotrader.com/' + link
        
        # Debug manually for car link doesn't available
        if url_link in ignore_w:
            continue
        
        car_link.append(url_link)
        # print('Check URL link: ', url_link)
        
        # Wait time for avoid banned
        # time.sleep(1) 
        
for item in car_link:
    # Using the try catch to handling some car doesn't available
    # try:
        # print('Check try')
        
        # Wait time for avoid banned
        time.sleep(1)
        
        # Get inside the real website where we can crawl the detail of a car
        page = requests.get(item)
        soup = BeautifulSoup(page.text, 'lxml')
        
        # Debug for some website dont have this element ( so we don't need Ignore list anymore )
        car_info = soup.select('div.text-left div.col-xs-10')
        if len(car_info) == 0:
            continue
        
        # Debug for finding location - TOFIGURE: Find value by key JSON not like this
        res = soup.find_all('script')
        for i, j in enumerate(res):
            if 'address1' in j.text:
                index = j.text.find('address1')
                add_info = j.text[index:index+40].split('",')[0].split(':"')[1]
                addresses.append(add_info.strip())
        
        # Debug for body_type
        for car in body_style:
            if car in item:
                type_car.append(car.capitalize().strip())
                seats.append(car_seats(car))
                
        
        # Update car model name & status & of the car
        car_model = soup.findAll('h1', class_ = 'text-bold')
        for car in car_model:
            car_name = car.text.split()
            status_car = car_name.pop(0)
            car_year = car_name.pop(0)
            name_car = ' '.join(car_name)
            if status_car == 'Used':
                status.append('1')
            elif status_car == 'Certified':
                status.append('-1')
            elif status_car == 'New':
                status.append('0')
            else:
                status.append('Unknown')
                
            years.append(car_year.strip())
            models.append(name_car.strip())
            
        # Wait time for avoid banned
        time.sleep(1)
            
        # Extract information in the box and append it into the list
        car_price = soup.select('span.first-price')
        for price in car_price:
            convert = currency_change(price.text)
            prices.append(convert)

        
        print('Length: ', len(car_info))
        print(item)
        # print(len(car_info))
        
        miles = car_info[0].text.split()[0]
        mile  = miles.replace(',', '.')
        car_km = convert_to_kmh(mile)
        convert_km = str(car_km).replace('.', ',')
        drive_km.append(convert_km.strip())
        
        # Wait time for avoid banned
        time.sleep(1)
        
        engine_type = car_info[1].text
        engine_trans = gg_trans.translate(engine_type).split()
        # print(engine_trans)
        chars = ['L']
        for i in range(len(engine_trans)):
            has_character = all([char in engine_trans[i] for char in chars])
            if engine_trans[i].lower() == 'xăng':
                engine_a.append('Xăng ')
            elif engine_trans[i].lower() == 'khí/điện' or engine_trans[i].lower() == 'lai:': 
                engine_a.append('Hybrid')
                engine_b.append('')
            elif engine_trans[i].lower() == 'điện':
                engine_a.append('Điện')
                engine_b.append('')
            elif engine_trans[i].lower() == 'linh':
                engine_a.append('Nhiên liệu linh hoạt ')
            elif engine_trans[i].lower() == 'diesel':
                engine_a.append('Diesel ')
            # else:
            #     print('Check this 6: ', engine_trans[i].lower())
            #     engine_a.append('Unknown')
            #     engine_b.append('')
            
            if has_character:
                engine_b.append(engine_trans[i])
            
        engine = [i + j for i, j in zip(engine_a, engine_b)]
        
        # Wait time for avoid banned
        time.sleep(1)
        
        # Get all the remain info and check for its string to append to the list
        for i in range(2, len(car_info)):
            name = car_info[i].text.strip()
            if 'Automatic Transmission' in name:
                gear.append('Số tự động')
            elif 'Manual Transmission' in name:
                gear.append('Số tay')
            
            if (city or highway) in name:
                citys.append(name.split()[0])
                highways.append(name.split()[3])
            elif 'Information Unavailable' in name:
                city_rpm = random.randint(15, 45)
                highway_rpm = random.randint(15, 45)
                if city_rpm > highway_rpm:
                    highway_rpm = city_rpm + random.randint(2, 7)
                citys.append(city_rpm)
                highways.append(highway_rpm)
            
            if awd in name:
                drive_shaft.append('AWD - 4 bánh toàn thời gian')
            elif fwd in name:
                drive_shaft.append('FWD - Dẫn động cầu trước')
            elif rfd in name:
                drive_shaft.append('RFD - Dẫn động cầu sau')   
            
            if exterior in name:
                remove_name = name.replace(exterior, '')
                color_out.append(gg_trans.translate(remove_name).capitalize())
                flag_out = True
            elif interior in name:
                remove_name = name.replace(interior, '')
                color_in.append(gg_trans.translate(remove_name).capitalize())
                flag_out = True
            
            # Debug for some pages don't have infomation for the exterior & interior
            if i == len(car_info) - 1:
                if not flag_in:
                    color_in.append('Unknown')
                if not flag_out:
                    color_out.append('Unknown')
                    
            # Debug for data
            for car in body_style:
                if car in item:
                    match car:
                        case 'sedan':
                            horse_power = random.randint(64, 175)
                            horsepowers.append(horse_power)
                            weight = random.randint(2140, 3131)
                            curbweights.append(weight)
                            base_round = round(random.uniform(94,121), 1)
                            wheelbases.append(base_round)
                            car_length = round(random.uniform(96, 121), 1)
                            carlengths.append(car_length)
                            car_height = round(random.uniform(47, 57), 1)
                            carheights.append(car_height)
                            engine_size = random.randint(108, 209)
                            enginesizes.append(engine_size)
                            bore_ratio = round(random.uniform(3, 3.79), 2)
                            boreratios.append(bore_ratio)
                            stroke = round(random.uniform(3, 3.4), 2)
                            strokes.append(stroke)
                            peak_rpm = random.randint(4200, 6600)
                            peakrpm.append(peak_rpm)
                        case 'hatchback':
                            horse_power = random.randint(48, 175)
                            horsepowers.append(horse_power)
                            weight = random.randint(1488, 2811)
                            curbweights.append(weight)
                            base_round = round(random.uniform(88, 103), 1)
                            wheelbases.append(base_round)
                            car_length = round(random.uniform(140, 180), 1)
                            carlengths.append(car_length)
                            car_height = round(random.uniform(49, 55), 1)
                            carheights.append(car_height)
                            engine_size = random.randint(61, 152)
                            enginesizes.append(engine_size)
                            bore_ratio = round(random.uniform(2.67, 3.8), 2)
                            boreratios.append(bore_ratio)
                            stroke = round(random.uniform(3, 3.5), 2)
                            strokes.append(stroke)
                            peak_rpm = random.randint(4200, 6600)
                            peakrpm.append(peak_rpm)
                        case 'wagon':
                            horse_power = random.randint(69, 155)
                            horsepowers.append(horse_power)
                            weight = random.randint(2024, 3042)
                            curbweights.append(weight)
                            base_round = round(random.uniform(94, 115), 1)
                            wheelbases.append(base_round)
                            car_length = round(random.uniform(157, 199), 1)
                            carlengths.append(car_length)
                            car_height = round(random.uniform(53, 60), 1)
                            carheights.append(car_height)
                            engine_size = random.randint(92, 183)
                            enginesizes.append(engine_size)
                            bore_ratio = round(random.uniform(2.92, 3.58), 2)
                            boreratios.append(bore_ratio)
                            stroke = round(random.uniform(2.18, 3.5), 2)
                            strokes.append(stroke)
                            peak_rpm = random.randint(4350, 5500)
                            peakrpm.append(peak_rpm)
                        case 'convertible':
                            horse_power = random.randint(90, 207)
                            horsepowers.append(horse_power)
                            weight = random.randint(2254, 2800)
                            curbweights.append(weight)
                            base_round = round(random.uniform(88, 98), 1)
                            wheelbases.append(base_round)
                            car_length = round(random.uniform(167, 180), 1)
                            carlengths.append(car_length)
                            car_width = round(random.uniform(48, 57), 1)
                            carwidths.append(car_width)
                            car_height = round(random.uniform(48, 57), 1)
                            carheights.append(car_height)
                            engine_size = random.randint(109, 234)
                            enginesizes.append(engine_size)
                            bore_ratio = round(random.uniform(2.68, 3.55), 2)
                            boreratios.append(bore_ratio)
                            stroke = round(random.uniform(2.67, 3.5), 2)
                            strokes.append(stroke)
                            peak_rpm = random.randint(4750, 7200)
                            peakrpm.append(peak_rpm)
                        case 'suv-crossover':
                            horse_power = random.randint(75, 250)
                            horsepowers.append(horse_power)
                            weight = random.randint(2255, 3137)
                            curbweights.append(weight)
                            base_round = round(random.uniform(80, 130), 1)
                            wheelbases.append(base_round)
                            car_length = round(random.uniform(105, 175), 1)
                            carlengths.append(car_length)
                            car_width = round(random.uniform(64, 75), 1)
                            carwidths.append(car_width)
                            car_height = round(random.uniform(73, 89), 1)
                            carheights.append(car_height)
                            engine_size = random.randint(85, 255)
                            enginesizes.append(engine_size)
                            bore_ratio = round(random.uniform(2.55, 3.44), 2)
                            boreratios.append(bore_ratio)
                            stroke = round(random.uniform(2.5, 3.7), 2)
                            strokes.append(stroke)
                            peak_rpm = random.randint(4500, 6300)
                            peakrpm.append(peak_rpm)
                        case 'coupe':
                            horse_power = random.randint(50, 200)
                            horsepowers.append(horse_power)
                            weight = random.randint(1655, 2653)
                            curbweights.append(weight)
                            base_round = round(random.uniform(67, 102), 1)
                            wheelbases.append(base_round)
                            car_length = round(random.uniform(94, 125), 1)
                            carlengths.append(car_length)
                            car_width = round(random.uniform(48, 58), 1)
                            carwidths.append(car_width)
                            car_height = round(random.uniform(51, 59), 1)
                            carheights.append(car_height)
                            engine_size = random.randint(75, 224)
                            enginesizes.append(engine_size)
                            bore_ratio = round(random.uniform(2.55, 3.9), 2)
                            boreratios.append(bore_ratio)
                            stroke = round(random.uniform(2.12, 3.57), 2)
                            strokes.append(stroke)
                            peak_rpm = random.randint(4850, 6800)
                            peakrpm.append(peak_rpm)
                        case 'van-minivan':
                            horse_power = random.randint(67, 187)
                            horsepowers.append(horse_power)
                            weight = random.randint(1453, 2735)
                            curbweights.append(weight)
                            base_round = round(random.uniform(55, 103), 1)
                            wheelbases.append(base_round)
                            car_length = round(random.uniform(89, 165), 1)
                            carlengths.append(car_length)
                            car_width = round(random.uniform(74, 90), 1)
                            carwidths.append(car_width)
                            car_height = round(random.uniform(65, 85), 1)
                            carheights.append(car_height)
                            engine_size = random.randint(75, 215)
                            enginesizes.append(engine_size)
                            bore_ratio = round(random.uniform(2.77, 3.25), 2)
                            boreratios.append(bore_ratio)
                            stroke = round(random.uniform(2.76, 3.87), 2)
                            strokes.append(stroke)
                            peak_rpm = random.randint(4100, 6500)
                            peakrpm.append(peak_rpm)
                        case 'truck':
                            horse_power = random.randint(105, 300)
                            horsepowers.append(horse_power)
                            weight = random.randint(2535, 3565)
                            curbweights.append(weight)
                            base_round = round(random.uniform(88, 127), 1)
                            wheelbases.append(base_round)   
                            car_length = round(random.uniform(152, 235), 1)
                            carlengths.append(car_length)
                            car_width = round(random.uniform(75, 110), 1)
                            carwidths.append(car_width)
                            car_height = round(random.uniform(73, 98), 1)
                            carheights.append(car_height)
                            engine_size = random.randint(150, 350)
                            enginesizes.append(engine_size)
                            bore_ratio = round(random.uniform(2.98, 3.99), 2)
                            boreratios.append(bore_ratio)
                            stroke = round(random.uniform(2.98, 4.2), 2)
                            strokes.append(stroke)
                            peak_rpm = random.randint(4900, 7500)
                            peakrpm.append(peak_rpm)
            
            
        # car_address = soup.select('div.row.padding-vertical-4')
        # print(car_address)
        
        
        origin.append('Xe nước ngoài')
        fuel_system.append('Unknown')
        
        # Wait time for avoid banned
        # time.sleep(1)
    # except:
        # print('Check Except')
        # continue

# for i in models:
#     print('Models: ', i)
# for i in years:
#     print('Years: ', i)
# for i in prices:
#     print('Prices: ', i)
# for i in origin:
#     print('Origin: ', i)
# for i in status:
#     print('Status: ', i)
# for i in type_car:
#     print('Type_car: ', i)
# for i in drive_km:
#     print('KMH: ', i)
# for i in color_out:
#     print('Color_out: ', i)
# for i in color_in:
#     print('Color in: ', i)
# for i in seats:
#     print('Seats: ', i)
# for i in engine:
#     print('Engine: ', i)
# for i in fuel_system:
#     print('Fuel_system: ', i)
# for i in gear:
#     print('Gear: ', i)
# for i in drive_shaft:
#     print('Shaft: ', i)
# for i in addresses:
#     print('Address: ', i)

zip_model = zip(models, years, prices, origin, status, type_car, drive_km, color_out, color_in, seats, 
                engine, fuel_system, gear, drive_shaft, citys, highways, wheelbases, carlengths, carwidths, 
                carheights, curbweights, enginesizes, boreratios, strokes, horsepowers, peakrpm, addresses)

# for i in zip_model:
#     print('Check Result: ', i)

for row in zip_model:
    f.writerow(row)
# out = GoogleTranslator(source = 'auto', target = 'vi').translate('Hello')
# print(out)

