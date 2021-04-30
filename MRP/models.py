from django.db import models
import datetime
from django.conf import settings

# Create your models here.
class Chemical(models.Model):
    uomlist = ( ('litre','litre'),
                ('grams','grams'),
                ('unit','unit'))

    part_num = models.CharField(max_length=200, primary_key=True, unique=True)
    chem_name = models.CharField(max_length=200,blank=True, null=True)
    leadtime = models.IntegerField(blank=True, null=True)
    std_packing = models.FloatField(blank=True, null=True)
    onhand = models.IntegerField(blank=True, null=True)
    chem_price = models.FloatField(blank=True, null=True)
    chem_class = models.IntegerField(blank=True, null=True)
    uom = models.CharField(max_length=100, choices=uomlist, default='litre' ,blank=True, null=True )
    STD_BOM = models.FloatField(blank=True, null=True)
    vendor_id = models.ForeignKey('Vendor', on_delete = models.CASCADE, blank=True, null=True )
    po_number = models.ForeignKey('PO', on_delete= models.CASCADE, blank=True, null=True )

    class Meta:
        ordering = ['part_num']
    
    #def __str__ (self):
     #   return self.part_num+'-'+self.chem_name+'-'+str(self.leadtime)+'-'+str(self.std_packing)+'-'+str(self.onhand)+'-'+str(self.chem_price)+'-'+str(self.chem_class)
    
class Vendor(models.Model):
    vendor_name = models.CharField(max_length=200)
    vendor_cont = models.EmailField(max_length = 254)
    def __str__(self):
        return self.vendor_name

class PO(models.Model):
    po_typelist = ( ('STD','STD'),
                    ('blanket','blanket'))
    po_number = models.CharField(max_length=200, primary_key= True  )
    po_type = models.CharField(max_length=100, choices = po_typelist, default='blanket')
    vendor_id = models.ForeignKey('Vendor', on_delete=models.CASCADE, blank=True, null=True)
    chem = models.ManyToManyField(Chemical)
    class Meta:
        ordering = ['po_number']
    def __str__(self):
        return self.po_number 


class Inv_PO(models.Model):
    po_number = models.ForeignKey('PO', on_delete=models.CASCADE, blank=True, null=True )
    part_num_id = models.ForeignKey('Chemical', on_delete=models.CASCADE, blank=True, null=True)
    #po_total = models.IntegerField(blank=True, null=True) 
    po_isin = models.BooleanField(blank=True, null=True)
    po_amount = models.IntegerField(blank=True, null=True)

class Inv_Chemical(models.Model):
    year = models.CharField(max_length=30, blank=True, null=True)
    month = models.CharField(max_length=20, blank=True, null=True)
    part_num = models.ForeignKey('Chemical',on_delete=models.CASCADE , blank=True, null=True )          
    chem_isin = models.BooleanField(blank=True, null=True)
    chem_amount = models.FloatField(blank=True, null=True)
    expired_date = models.DateField(blank=True, null=True)
    record_date = models.DateTimeField(auto_now=True)
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE,blank=True, null=True)
    #user_id = foreignkey
    def __str__(self):
        return self.year+"-"+self.month+"-"+str(self.chem_amount)


class WeekLoading(models.Model):
    week = models.CharField(max_length=100, blank=True, null=True )
    loading = models.IntegerField(blank=True, null=True)
    package_id = models.ForeignKey('Package', on_delete=models.CASCADE, blank=True, null=True)
    def __str__(self):
        return str(self.package_id)+"-"+self.week+"-"+str(self.loading)
    
class Package(models.Model):
    #type_list = (   ('TSOP','TSOP'),
                    #('LGA', 'LGA'))
    #package_type = models.CharField(max_length=100, choices=type_list, default='TSOP', blank=True, null=True )
    package_name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.package_name

class Status_Chem(models.Model):
    statuslist = (  ('shortage','shortage'),
                    ('enough','enough'))
    chem_status = models.CharField(max_length=100, choices=statuslist, default='enough')
    listchem = models.ForeignKey('Chemical',on_delete=models.CASCADE, blank=True, null=True)
    #chemical = models.ManyToManyField('Chemical')
    #class Meta:
     #   ordering = ['chem_status']
    def __str__(self):
        return self.chem_status

#class ShowStatus(models.Model):
 #   part_num = models.ForeignKey('Chemical', on_delete=models.CASCADE, blank=True, null=True )
  #  status_id = models.ForeignKey('Status_Chem', on_delete=models.CASCADE, blank=True, null=True)
   # ROP = models.FloatField(blank=True, null=True)

class EoqBoqload(models.Model):
    year = models.CharField(max_length=30, blank=True, null=True)
    month = models.CharField(max_length=30, blank=True, null=True)
    loading = models.IntegerField(blank=True, null = True)
    #package_iid = models.ForeignKey('Package',on_delete=models.CASCADE, blank=True, null=True )
    def __str__(self):
        return self.year+'-'+self.month+'-'+str(self.loading)


    







    




