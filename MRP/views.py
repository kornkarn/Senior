from django.shortcuts import render, redirect
import openpyxl
from django.contrib.auth.models import User, auth
from django.contrib import messages 
from django.contrib.auth.decorators import login_required
from .models import *
from .filters import ChemicalFilter, WeekFilter

# Create your views here.


def HomePage(request):
    return render(request, 'homepage.html')

def Register(request):
    if request.method == "POST" :
        data = request.POST.copy()
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        password = data.get('password')

        newuser = User()
        newuser.username = email
        newuser.first_name = first_name
        newuser.last_name = last_name 
        newuser.email = email
        newuser.set_password(password)
        newuser.save() 

        return redirect('home-page')


    return render(request, 'register.html')

@login_required
def FileUpLoad(request):
    return render(request, 'fileupload.html')

@login_required
def Material(request):
    chemical = Chemical.objects.all()
    vendor = Vendor.objects.all()
    po = PO.objects.all()
    inv_chem = Inv_Chemical.objects.all()
    if request.method == "POST" :
        data = request.POST.copy()
        deletecheck = data.getlist('check')
        for i in deletecheck :
            Chemical.objects.filter(part_num = i).delete()
            ####ทำให้มันลบ po กับ vendor ด้วยอย่าให้มันลบแค่สารเคมี
        
        
    return render(request, 'material.html', {'chemical':chemical,'vendor':vendor,'po': po,'inv_chem':inv_chem})
def AddMaterial(request):
    if request.method == "POST":
        data = request.POST.copy()
        partnumber = data.get('partnumber')
        chemname = data.get('chemname')
        leadtime = data.get('leadtime')
        stdpack = data.get('stdpack')
        price = data.get('price')
        chemclass = data.get('chemclass')
        onhand = data.get('onhand')
        uom = data.get('uom')
        stdbom = data.get('stdbom')
        #below are not include in db chemical table
        vendorname = data.get('vendorname') #vendor Table
        emailvendor = data.get('emailvendor')  #Vendor Table
        ponum = data.get('ponum') #!!!!ต้องมา design ตาราง PO ที่เป็นแบบ static ว่าจะให้เก็บข้อมูลอะไรบ้าง
        expdate = data.get('expdate') #เข้าไปอยู่ใน inventory
        
        newvendor = Vendor()
        newvendor.vendor_name = vendorname
        newvendor.vendor_cont = emailvendor
        newvendor.save() 

        newpo = PO()
        newpo.po_number = ponum
        newpo.save() 

        newchem = Chemical()
        newchem.part_num = partnumber
        newchem.chem_name = chemname
        newchem.leadtime = leadtime
        newchem.std_packing = stdpack
        newchem.onhand = onhand
        newchem.chem_price = price
        newchem.chem_class = chemclass
        newchem.uom = uom
        newchem.STD_BOM = stdbom
        newchem.vendor_id = newvendor
        newchem.po_number = newpo
        newchem.save()


        new_invchem = Inv_Chemical()
        new_invchem.expired_date = expdate
        new_invchem.save()


        return redirect('material-page')

    return render(request, 'Add_material.html')

def WeekLoad(request):
    if request.method == "POST":
        excel_file = request.FILES["excel_file"]
        wb = openpyxl.load_workbook(excel_file)
        worksheet = wb["CAP"]

        week_n = worksheet['D5'].value[2:4]+"'"+worksheet['D5'].value[5:7]
        week_n1 = worksheet['G5'].value[2:4]+"'"+worksheet['G5'].value[5:7]
        week_n2 = worksheet['J5'].value[2:4]+"'"+worksheet['J5'].value[5:7]
        week_list = [week_n, week_n1, week_n2]

        #TS040/48 week n
        max1 = max(worksheet['C10'].value,worksheet['D10'].value)
        #TS040/48 week n+1
        max2 = max(worksheet['F10'].value,worksheet['G10'].value)
        #TS040/48 week n+2
        max3 = max(worksheet['I10'].value,worksheet['J10'].value)

        #TS056 week n
        max4 = max(worksheet['C11'].value,worksheet['D11'].value)
        #TS056 week n+1
        max5 = max(worksheet['F11'].value,worksheet['G11'].value)
        #TS056 week n+2
        max6 = max(worksheet['I11'].value,worksheet['J11'].value)

        data_list = [max1,max2,max3,max4,max5,max6] 
        package = Package.objects.all() 
        
        x = 0
        for p in package:
            for w in week_list:
                newload = WeekLoading()
                newload.package_id = p
                newload.week = w
                newload.loading = data_list[x]
                x += 1   
                newload.save()

    
        return render(request,'Add_weekloading.html',{'data_list': data_list} )

    return render(request, 'Add_weekloading.html')

#planing ให้ลองrun ดูว่าต้องสั่งมั้ย เอา forecast ที่ได้เเต่ละวีคมาปรับเเล้วลองรันดู
def Planning(request):
    
    if request.method == "POST":
        searchchem = request.POST['searchchem']
        weekstart = request.POST['weekstart']
        weekend = request.POST['weekend']
        chem_data = Chemical.objects.filter(chem_name=searchchem)
        week_load = WeekLoading.objects.all()
        package = Package.objects.all() 
        actual = Inv_Chemical.objects.all()

        each_week_after_search = []
        def myFunc(e):
            return e[3:5]
        each_week = sorted(WeekLoading.objects.values_list('week', flat = True).distinct())
        each_week.sort(key = myFunc)
        for w in range(len(each_week)) : #เอาเเค่วีคที่ search
            if each_week[w] == weekstart :
                start = w 
            if each_week[w] == weekend :
                end = w
        each_week_after_search = each_week[start:end+1]
     
        #actual usage in this chemical (ต้องหาก่อนว่าวีคนั้นอยู่เดือนไร,ปีไร เเล้วเอา actual มาหารจำนวนวีค)
        numweek_in_each_month = [4,4,5,4,4,5,4,4,5,4,4,5] 
        actual_each_week = []
        for ac in each_week: #22'20
            week = int(ac[:2])
            for n in range(len(numweek_in_each_month)) :
                week -= numweek_in_each_month[n]
                if week == 0 :
                    #print(n+1)
                    break
                if week < 0 :
                    #print(n+1)
                    break
            act = actual.filter(year = '20'+ac[3:], month = n+1, part_num=Chemical.objects.get(chem_name=searchchem).part_num).values_list('chem_amount', flat=True)
            if len(act) == 0 :
                actual_each_week.append("")
            else :
                actual_each_week.append(int(act[0]/numweek_in_each_month[n]))
        actual_after_search = actual_each_week[start:end+1]
      
        #forecast_adjust
        month = []
        year = []
        balance = []
        onhand = [2000]

        #check ว่า week นั้นอยู่เดือนไหน
        for w in each_week:
            if ('20'+w[3:]) not in year :
                year.append('20'+w[3:])
        
        adj_forecast = []

        #adjust forecast by week
        for i in each_week :
            wi = int(i[:2])
            yi = i[3:]
            for n in range(len(numweek_in_each_month)):
                wi -= numweek_in_each_month[n]
                if wi == 0 :
                    #print(n+1)
                    break
                if wi < 0 :
                    #print(n+1)
                    break
            adj = []
            for y in year :
                if y[2:] < yi :
                    ac = actual.filter(year = y, month = n+1, part_num= Chemical.objects.get(chem_name=searchchem).part_num).values_list('chem_amount', flat=True)
                    sumload_thischem = 0
                    for p in package : 
                        sumload_thischem += week_load.filter(week = i[:2]+"'"+y[2:]).filter(package_id = p).values_list('loading', flat = True).last()
                    diff = (ac[0]/numweek_in_each_month[n])-(sumload_thischem * Chemical.objects.get(chem_name=searchchem).STD_BOM)
                    adj.append(diff)
            
            if adj != [] :
                sumload = 0
                for p in package :
                    sumload += week_load.filter(week = i[:2]+"'"+yi).filter(package_id = p).values_list('loading', flat = True).last()
                adj_forecast.append(int((sumload * Chemical.objects.get(chem_name=searchchem).STD_BOM)+(sum(adj)/len(adj))))
                #print(adj_forecast)
            if yi == year[0][2:] :
                sumload_thischem = 0
                for p in package : 
                    sumload_thischem += week_load.filter(week = i[:2]+"'"+yi).filter(package_id = p).values_list('loading', flat = True).last()
                adj_forecast.append(int(sumload_thischem * Chemical.objects.get(chem_name=searchchem).STD_BOM))
        adj_forecast_after_search = adj_forecast[start:end+1]

        
        #balance = onhand - usage + order recieve
        for x in range(len(adj_forecast)):
            if actual_each_week[x] != "" and len(actual_each_week) >= x :
                if balance == [] :
                    bal = onhand[0] - actual_each_week[x]
                    balance.append(bal)
                else :
                    bal = balance[-1] - actual_each_week[x]
                    balance.append(bal)
            else :
                if balance == [] :
                    bal = onhand[0] - adj_forecast[x]
                    balance.append(bal)
                else :
                    bal = balance[-1] - adj_forecast[x]
                    balance.append(bal)
        balance_after_search = balance[start:end+1]

        #check ว่า shortage มั้ย
        order_release = [] #อาจจะให้เก็บ ความยาวเท่ากับ each_week แล้วข้างในเป็น "" หมดเลย
        order_receive = []
        week_policy1 = [1,5,9,14,18,22,27,31,35,40,44,48,1] #กรณีที่สั่งสัปดาห์ที่1
        week_policy2 = [2,6,10,15,19,23,28,32,36,41,45,49,2] #กรณีที่สั่งสัปดาห์ที่2

        for i in range(len(each_week)) :
            if (int(each_week[i][:2])-7) in week_policy1 : #กรณีลงสัปดาห์ที่ 1
                if balance[i] <= 0  :  #or inventory position ตัวที่ i-1 < forecast ตัวที่ i
                    week_order = int(each_week[i][:2]) - 7
                    order_quan = sum(adj_forecast[i+1:i+6])
                    order_release[week_order] = order_quan
                    #คิด new balance
            else :
                for n in range(len(week_policy2)) : #กรณีลงสัปดาห์ที่ 2
                    if int(each_week[i][:2])-7 < week_policy2[n] :
                        week_order = week_policy2[n-1] #ต้องไปอัพเดทใน database ด้วยว่า status มัน short
                        break
                    if int(each_week[i][:2])-7 = week_policy2[n] :
                        week_order = week_policy2[n]
                        break
                order_quan = sum(adj_forecast[i+1:i+6])
                order_release[week_order] = order_quan   #ต้องมีคิด SS บวกเข้าไปด้วย
            
                
        """
        for i in range(len(each_week)) :  
            if balance[i] <= 0 : #ดูว่าอยู่ week policy มั้ย ex.26 สั่งย้อนไป 7 วีค
                for n in range(len(week_policy)): 
                    if int(each_week[i][:2])-7 < week_policy[n] :
                        week_order = week_policy[n-1]
                        break
                order_quan = sum(adj_forecast[i+1:i+6])
                order_release.append(order_quan)  #append ค่า order quantity 
                for b in range(len(balance[i:])) :
                    if actual_each_week[i] != "" :
                        balance[i+b] = balance[i-1] - actual_each_week[i] + order_quan 
                    else :
                        balance[i+b] = balance[i-1] - adj_forecast[i] + order_quan          
            else :
                order_release.append("")
                order_receive.append("")

        for i in range(len(order_release)) : #เขียนให้ order receive มันห่างกับ release 7 วีค
            print(i)
            if order_release[i] == "" :
                order_receive.append("")
            else :
                for j in range(7) :
                    if j != 6 :
                        order_receive.append("")
                    else :
                        order_receive.append(order_release[i])
                        
                       
                    
        print(order_release)
        print(order_receive)
        print(balance)
        """
        #inventory position = balance + plan receive ของ 7 วีคข้างหน้า

        #ถ้ามี order ให้ขึ้นไปที่หน้า dashboard ด้วย 



        return render(request, 'Planning_table.html', {'chem_data':chem_data,'order_release':order_release, 'start':start,'balance_after_search':balance_after_search, 'end':end, 'each_week_after_search':each_week_after_search, 'adj_forecast_after_search':adj_forecast_after_search, 'actual_after_search':actual_after_search, 'onhand':onhand, 'balance':balance})

            
    return render(request, 'Planning_table.html')

def ActualUsage(request):
    if request.method == "POST":
        y = request.POST['year']
        excel_file = request.FILES["excel_file"]
        wb = openpyxl.load_workbook(excel_file, data_only=True)
        worksheet = wb["USAGE"]

        num = 0
        for row in range(3,4):
            for col in range(1,16):
                if worksheet.cell(row,col).value == 0  :
                    num = col
                    break
                else :
                    num = 16
        
        partnum = []
        for row in range(3,24):
            for col in range(1,num):
                if col != 2 and col != 3 :
                    if col == 1 :
                        partnum.append(worksheet.cell(row,col).value)
                        #print(part_num)
                    else : 
                        chemamount = float(worksheet.cell(row,col).value)
                        c = Inv_Chemical(year = y, month = str(col-3), chem_isin = False, chem_amount= chemamount, part_num_id = partnum[-1])
                        c.save()
        #check ก่อนว่า file ชื่อเดียวกันไหม ถ้าชื่อเดียวกันก็ขึ้นว่าเคยอัพโหลดไฟล์นี้เเล้ว    
                        #print(amount)
        #Inv_Chemical.objects.all().delete()
        print(num)
        
    return render(request, 'Add_actualusage.html')

def EoqBoq(request):
    if request.method == "POST":
        allpackage = Package.objects.all()
        data = request.POST.copy()
        y = data.get('year')
        m = data.get('m')
        q = data.get('q')
        lga = data.get('lga')
        ts048 = data.get('ts048')
        ts056 = data.get('ts056')
    

        if request.POST['q'] == '' :
            eoqboq = EoqBoqload(year = y, month = m, loading = 40/48 * int(lga) + int(ts048) + 56/48 * int(ts056) )
            eoqboq.save()
        
        else : 
            end = (int(q)*3)+1
            for i in range(end-3,end):
                eoqboq = EoqBoqload(year = y, month = i , loading = (40/48 * int(lga) + int(ts048) + 56/48 * int(ts056))//3 )
                eoqboq.save()
              
            #ถ้ามันรวมมาเป็น quater เราเเยกครึ่งๆเลยได้ใช่มั้ยว่ามาจาก TS048 ครึ่งนึง TS056 ครึ่งนึง
        return render(request, 'Add_eoqboq.html')
            
    
    return render(request, 'Add_eoqboq.html')

def DashBoard(request):
    chemical = Chemical.objects.all()
    status = Status_Chem.objects.all()
    enough = []
    shortage = []
    #check status and show colour sign
    for i in range(len(status)) :
        for j in status[i].chemical.all() :
            if i == 0 :
                enough.append(j.part_num)
            if i == 1 :
                shortage.append(j.part_num)
              
    
    return render(request,'dashboard.html', {'chemical':chemical, 'status':status, 'enough':enough, 'shortage':shortage})

def UpdateMaterial(request, part_num):
    if request.method == "POST":
        data = request.POST.copy()
        partnumber = data.get('partnumber')
        chemname = data.get('chemname')
        leadtime = data.get('leadtime')
        stdpack = data.get('stdpack')
        price = data.get('price')
        chemclass = data.get('chemclass')
        onhand = data.get('onhand')
        uom = data.get('uom')
        stdbom = data.get('stdbom')
        vendorname = data.get('vendorname')
        emailvendor = data.get('emailvendor') 
        ponum = data.get('ponum') 
        expdate = data.get('expdate') 
        vendor_update = Vendor(vendor_name=vendorname, vendor_cont=emailvendor)
        vendor_update.save()
        po_update = PO(po_number=ponum)
        po_update.save()
        chem_update = Chemical( part_num = partnumber, chem_name= chemname, leadtime= leadtime, 
                                std_packing= stdpack, chem_price= price, chem_class=chemclass, 
                                onhand= onhand, uom=uom, STD_BOM= stdbom, vendor_id=vendor_update, po_number = po_update)
        chem_update.save()
        return redirect('material-page')
        
    getchem = Chemical.objects.get(part_num = part_num)
    return render(request, 'updatemat.html', {'getchem':getchem})