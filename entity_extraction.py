import re
# import pandas as pd
from converter import zg12uni51

zawgyiReg = '\u1031\u103b|^\u1031|^\u103b|[\u1022-\u1030\u1032-\u1039\u103b-\u103d\u1040-\u104f]\u103b|\u1039$|\u103d\u103c|\u103b\u103c|[\u1000-\u1021]\u1039[\u101a\u101b\u101d\u101f\u1022-\u102a\u1031\u1037-\u1039\u103b\u1040-\u104f]|\u102e[\u102d\u103e\u1032]|\u1032[\u102d\u102e]|[\u1090-\u1099][\u102b-\u1030\u1032\u1037\u103c-\u103e]|[\u1000-\u102a]\u103a[\u102c-\u102e\u1032-\u1036]|[\u1023-\u1030\u1032-\u1039\u1040-\u104f]\u1031|[\u107e-\u1084][\u1001\u1003\u1005-\u100f\u1012-\u1014\u1016-\u1018\u101f]|\u1025\u1039|[\u1081\u1083]\u108f|\u108f[\u1060-\u108d]|[\u102d-\u1030\u1032\u1036\u1037]\u1039|\u102c\u1039|\u101b\u103c|[^\u1040-\u1049]\u1040\u102d|\u1031?\u1040[\u102b\u105a\u102e-\u1030\u1032\u1036-\u1038]|\u1031?\u1047[\u102c-\u1030\u1032\u1036-\u1038]|[\u102f\u1030\u1032]\u1094|\u1039[\u107E-\u1084]'

make_reg      = r'acura|audi|bentley|bmw|buick|cadillac|chevrolet|chrysler|citeron|dodge|daihatsu|fiat|ford|gmc|honda|hyundai|infiniti|isuzu|jaguar|jeep|kia|land rover|lexus|lincoln|maserati|mazda|mercedes|mini|mitsubishi|nissan|peugeot|range rover|renault|subaru|suzuki|tesla|toyota|vauxhall|volkswagen|volvo'
except_reg    = r'\W+|luxury|sedan|hatchback|hybrid|coupe|suv|convertible|minivan|wagon|pickup|truck|mingalar|myanmar|brand|[က-အ]+'
model_reg     = r'model'
grade_reg     = r'grade'
year_reg      = r'[1][9][9][0-9]|[2][0][0-9][0-9]|model|year'
engine_reg    = r'\d{4} cc|\d{4}. cc|\d{4}cc|\d{4}.cc|[1-4]\.[0-9] cc|[1-4]\.[0-9]. cc|[1-4]\.[0-9]cc|1-4]\.[0-9].cc|\b[1-4]\.[0-9]\b'
color_reg     = r'pearl white|black|dark grey|white|silver|gray|blue' 
body_reg      = r'sedan|hatchback|hybrid|coupe|suv|convertible|minivan|wagon|pickup|truck'
drive_reg     = r'4x4|\dw|\dwd|\d wd|\d wheel||\dwheel|\dweel|\d weel'
fuel_reg      = r'diesel|petrol|ဓာတ်ဆီ|ဒီဇယ်'
mileage_reg   = r'km|kilo|mileage|milage|ကိလို|ကီလို'
gear_reg      = r'auto|manual|gear'
region_reg    = r'ygn|mdy|shn|sgg|bgo|shn|npw|ayy'
seater_reg    = r'seater|seaters|seating'
hand_reg      = r'ဘယ်မောင်း|ညာမောင်း|l.h.d|r.h.d|lhd|rhd'
license_reg   = r'\d[a-z]\/|\d[a-z] \/|\d[a-z]\-|\d[a-z] \-|number|license|licence|လိုင်စင်|ygn|mdy|shn|sgg|bgo|shn|npw|ayy'
price_reg     = r'price|သိန်း'
    
def get_entity(post_text):
    post_list = post_text.split('\n')
    segment = {}
    segment['brand']        = '-'   ## honda,toyota
    segment['name']         = '-'   ## fit, corolla
    segment['model']        = '-'   ## 
    segment['price']        = '-'   ## 340 lakhs
    segment['grade']        = '-'   ## xs, full
    segment['year']         = '-'   ## 1999,2008
    segment['engine']       = '-'   ## 2000 cc,1300 cc
    segment['color']        = '-'   ## peral white, black
    segment['body_type']    = '-'   ## sedan,hatchback
    segment['wheel_drive']  = '-'   ## 2,4
    segment['fuel']         = '-'   ## petrol,diesel
    segment['mileage']      = '-'   ## 14000 km
    segment['gear']         = '-'   ## auto, manual
    segment['seater']       = '-'   ## 6-seater, 7-seater
    segment['hand_drive']   = '-'   ## RHD, LHD
    segment['region']       = '-'   ## mdy, ygn, bgo,
    segment['license-initial']      = '-'   ## 9n/****, 
    
    
    for line in post_list:
        line = line.lower()
        if (len(line) > 120):
            continue
        else:
            if re.search(make_reg, line):
                segment['brand'] = re.search(make_reg, line).group()

                if segment['name'] == '-':
                    try:
                        model = line.split()[1]
                        if re.search(except_reg, model):
                            pass
                        elif model == 'mark':
                            segment['name'] = 'mark-2'
                        else:
                            segment['name'] = model
                    except:
                        segment['name'] = '-'

            if segment['year'] == '-' and re.search(year_reg, line):
                if re.search(r'[က-အ]', line) or line.startswith('ph') or line.startswith('09'):
                    pass
                else:
                    if re.search(r'[1][9][9][0-9]|[2][0][0-9][0-9]',line):
                        segment['year'] = re.search(r'[1][9][9][0-9]|[2][0][0-9][0-9]',line).group()
                        
                    elif re.search(r'model', line) and segment['model'] == '-':
                        model = line.replace('model','').strip()
                        segment['model'] = re.sub(r'\W+','',model).strip()
                    else:
                        segment['model'] = '-'

            if (segment['grade'] == '-') and (re.search(grade_reg, line)):
                try:
                    grade_ = re.sub('\W+',' ', line )  #remove special char
                    grade_lst = grade_.split()
                    grade_str = ''
                    for g in grade_lst:
                        if re.search('grade|\d+|model|[က-အ]|\/',g):
                            pass
                        else:
                            grade_str += g
                    segment['grade'] = re.sub('\W+','',grade_str)
                except:
                    segment['grade'] = '-'

            if segment['color'] == '-' and re.search(color_reg, line):
                segment['color'] = re.search(color_reg, line).group()

            if (segment['body_type'] == '-') and (re.search(body_reg,line)):
                segment['body_type'] = re.search(body_reg, line).group()

            if (segment['wheel_drive'] == '-') and (re.search(drive_reg,line)):
                try:
                    drive_train = re.search(drive_reg, line).group()
                    segment['wheel_drive'] = re.search(r'\d', drive_train).group() + ' wheel'
                except:
                    segment['wheel_drive'] = '-'    

            if segment['fuel'] == '-' and re.search(fuel_reg,line):
                fuel_type = re.search(fuel_reg, line).group()
                if fuel_type == 'ဓာတ်ဆီ':
                    segment['fuel'] = 'petrol'
                elif fuel_type == 'ဒီဇယ်':
                    segment['fuel'] = 'diesel'
                else:
                    segment['fuel'] = fuel_type

            if segment['engine'] == '-' and re.search(engine_reg, line):
                engine = re.search(engine_reg, line).group()
                displacement = float(re.search(r"\d+(\.\d+)?", engine).group())
                if displacement <100:
                    displacement *=1000
                segment['engine']= str(int(displacement)) + ' cc'

            if segment['price'] == '-' and re.search(price_reg, line):
                try:
                    price = re.search(r"\d+", line).group()

                    if len(price) >2:
                        new_str = ''
                        for i in price:
                            if 4160 <= ord(i) <=4170:
                                new_str += str(ord(i)%10)
                            else:
                                new_str += i
                        segment['price'] = new_str+' Lakhs'
                    else:
                        segment['price'] = '-'
                except:
                    segment['price'] = '-'

            if segment['mileage'] == '-' and re.search(mileage_reg, line):
                if re.search(r'\d+\,\d+', line):                                ## 140,000
                    segment['mileage'] = re.search(r'\d+\,\d+', line).group().replace(',','') + ' km'
                elif re.search(r'\d+ \+|\d+\+', line):                          ## 150000 + , 150,000+
                    segment['mileage'] = re.search(r'\d+ \+|\d+\+', line).group().strip('+').strip() + ' km'
                else:
                    try:
                        array = re.findall(r'\d+|\++|[x]+|\*+|သောင်း|သိန်း',line)  ## 1++++ , 3xxxxx, 4*****, 2 သိန်း
                        km = ''.join(array)
                        if km.find(',') >=0:
                            mileage = km.replace(',','')
                        elif km.find('+') >=0:
                            mileage = km.replace('+', '0')
                        elif km.find('x') >=0:
                            mileage = km.replace('x', '0')
                        elif km.find('*') >=0:
                            mileage = km.replace('*', '0')
                        elif km.find('သောင်း') >=0 :
                            mileage = km.replace('သောင်း', '0000')
                        elif km.find('သိန်း') >=0 :
                            mileage = km.replace('သိန်း','00000')
                        else:
                            mileage = km
                        if len(mileage)<7:
                            new_str = ''
                            for i in mileage:
                                if 4160 <= ord(i) <=4170:
                                    new_str += str(ord(i)%10)
                                else:
                                    new_str += i
                            segment['mileage'] = new_str+' km'
                        else:
                            segment['mileage'] = '-'

                    except:
                        segment['mileage'] = '-'

            if (segment['region'] == '-') and (re.search(region_reg,line)):
                try:
                    segment['region'] = re.search(region_reg,line).group()
                except:
                    segment['region'] = '-'


            if (segment['gear'] == '-') and (re.search(drive_reg, line)):
                if ( line.find('auto') > 0 ):
                    segment['gear'] = 'auto'
                elif ( line.find('manual') > 0 ):
                    segment['gear'] = 'manual'
                else:
                    segment['gear'] = '-'

            if (segment['seater'] == '-') and (re.search(seater_reg, line)):
                try:
                    segment['seater'] = re.findall(r'\d',line)[0] + ' seats'
                except:
                    segment['seater'] = '-'
                    
            if (segment['hand_drive'] == '-') and (re.search(hand_reg,line)):
                drive_postion = re.search(hand_reg,line).group()
                
                if drive_position == 'ဘယ်မောင်း' or drive_postion == "l.h.d" or drive_postion =="lhd":
                    segment['hand_drive'] = 'L.H.D'
                if drive_position == 'ညာမောင်း' or drive_postion == "r.h.d" or drive_postion == "rhd":
                    segment['hand_drive'] = 'R.H.D'
                    
            if (segment['license-initial']== '-' ) and (re.search(license_reg,line)):
                license = re.sub(r'[က-႟]|[၀-၉]|license|licence|number|no|ygn|mdy|shn|bgo|sgg','',line)
                segment['license-initial'] = re.sub(r'\d+\.\d+\.\d+|\d+\/\d+\/\d+|\d+\-\d+\-\d+|\d+\.\d+|\d+\/\d+|\d+\-\d+','' ,license)
    return segment              

def isZawGyi(text):
    if (re.search(zawgyiReg,text) != None):
        return True
    return False

def toUnicode(text):
    return (zg12uni51(input_text = text))
       
def retrieve_entity(post):
    sentence = (str(post)+'\n\n')
    zawgyi = isZawGyi(sentence)
    if zawgyi:
        standard = toUnicode(sentence)
    else:
        standard = sentence
    entity_list = get_entity(standard)
    return entity_list