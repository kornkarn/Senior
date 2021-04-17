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
        chem_data = Chemical.objects.filter(chem_name=searchchem)
        week_load = WeekLoading.objects.all()
        package = Package.objects.all() 
        actual = Inv_Chemical.objects.all()

        def myFunc(e):
            return e[3:5]
        each_week = sorted(WeekLoading.objects.values_list('week', flat = True).distinct())
        each_week.sort(key = myFunc)
        #print(each_week) 
            
        #sumloading 
        sum_each_week = []
        for w in each_week :
            total = 0
            for p in package :
                total += week_load.filter(week = w).filter(package_id = p).values_list('loading', flat = True).last()
            sum_each_week.append(total)
        
        #forecast usage in this chemical
        forecast_usage_each_chem = []
        for i in sum_each_week :
            forecast_usage_each_chem.append(Chemical.objects.get(chem_name=searchchem).STD_BOM * i)

        #actual usage in this chemical (ต้องหาก่อนว่าวีคนั้นอยู่เดือนไร,ปีไร เเล้วเอา actual มาหารจำนวนวีค)
        numweek_in_each_month = [4,4,5,4,4,5,4,4,5,4,4,5] #ไม่ใช่ละต้องเป็น [4,5,4,4,5,4,4,5,4,4,5,4]
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
                actual_each_week.append(0)
            else :
                actual_each_week.append(act[0]/numweek_in_each_month[n])
        print(actual_each_week)
            

        #forecast_adjust
        forecast_adjust = [] 
        month = []
        year = []
        balance = []
        onhand = [1000]

        #check ว่า week นั้นอยู่เดือนไหน
        for w in each_week:
            if ('20'+w[3:]) not in year :
                year.append('20'+w[3:])
    
        #adjust forecast
        for i in range(len(each_week)): #22'20
            weekk = int(each_week[i][:2])
            for n in range(len(numweek_in_each_month)) :
                weekk -= numweek_in_each_month[n]
                if weekk == 0 :
                    #print(n+1)
                    break
                if weekk < 0 :
                    #print(n+1)
                    break
            average_adjust = []
            for y in year :
                if int(y[2:]) < int(each_week[i][3:]) :
                    actual_each_month = actual.filter(year = y, month = n+1, part_num=Chemical.objects.get(chem_name=searchchem).part_num ).values_list('chem_amount', flat = True)
                    convert_to_week = actual_each_month[0]/numweek_in_each_month[n]
                    #print(convert_to_week)
                    for k in range(int(numweek_in_each_month[n])): #5 เอา forecast แต่ละวีคมาลบ actual 22,23,24,25,26
                        ww = 0
                        for l in numweek_in_each_month[:n] :
                            ww += int(l)
                        ww += 1+k
                        #print(ww)
                        sumloading_each_week = 0
                        for p in package :
                            sumloading_each_week +=  week_load.filter(week = str(ww)+"'"+y[2:]).filter(package_id = p).values_list('loading', flat = True).last()
                        #print(sumloading_each_week)
                        average_adjust.append(convert_to_week - sumloading_each_week*(Chemical.objects.get(chem_name=searchchem).STD_BOM))
            #print(i)
            #print(average_adjust, sum(average_adjust), len(average_adjust)) 
            if average_adjust != [] :
                forecast_adjust.append(sum_each_week[i]*(Chemical.objects.get(chem_name=searchchem).STD_BOM) + (sum(average_adjust)/len(average_adjust)))
            else :
                forecast_adjust.append(sum_each_week[i]*(Chemical.objects.get(chem_name=searchchem).STD_BOM) + 0)
        #print(forecast_adjust)
                    #ลองเอาตัวเลขมารันดูใน excelว่าได้มั้ย
        
        #balance = onhand - usage + order recieve
        for x in range(len(forecast_adjust)):
            if actual_each_week[x] != 0 and len(actual_each_week) >= x :
                if balance == [] :
                    bal = onhand[0] - actual_each_week[x]
                    balance.append(bal)
                else :
                    bal = balance[-1] - actual_each_week[x]
                    balance.append(bal)
            else :
                if balance == [] :
                    bal = onhand[0] - forecast_adjust[x]
                    balance.append(bal)
                else :
                    bal = balance[-1] - forecast_adjust[x]
                    balance.append(bal)
        print(balance)
            

        #find order received

        #week filter
        wl = WeekLoading.objects.all()
        wlfilter = WeekFilter(request.GET, queryset=wl)
        #print(wl)


        return render(request, 'Planning_table.html', {'chem_data':chem_data, 'each_week':each_week, 'forecast_usage_each_chem':forecast_usage_each_chem, 'actual_each_week':actual_each_week, 'wlfilter':wlfilter, 'balance':balance, 'forecast_adjust':forecast_adjust})

            
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