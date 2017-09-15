from django.db import models

class CableTvType(models.Model):
    type = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.type

class CableTvSource(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class CableTvDistrict(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class CableTvQuarter(models.Model):
    number = models.PositiveIntegerField()

    def __str__(self):
        return str(self.number)

class CableTvZone(models.Model):
    name = models.CharField(max_length=20, null=True)
    district = models.ForeignKey(CableTvDistrict)
    quarter = models.ManyToManyField(CableTvQuarter)
    comment = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return str(self.name)

class CableTvCat(models.Model):
    cat = models.ForeignKey(CableTvSource, verbose_name=(u'Категория'))
    zone = models.ForeignKey(CableTvZone, null=True)
    type = models.ForeignKey(CableTvType, null=True)

    def __str__(self):
        return str(self.cat) + '-' + str(self.zone) + '(' + str(self.type) + ')'

class CableTvPouch(models.Model):
    name = models.OneToOneField(CableTvCat, null=True)
    balance = models.IntegerField(default=0)

    def __str__(self):
        return str(self.name)

class CableTvResult(models.Model):
    month = [
        ('Январь', 'Jan'),
        ('Февраль', 'Feb'),
        ('Март', 'March'),
        ('Апрель', 'Apr'),
        ('Май', 'May'),
        ('Июнь', 'June'),
        ('Июль', 'July'),
        ('Август', 'Aug'),
        ('Сентябрь', 'Sept'),
        ('Октябрь', 'Oct'),
        ('Ноябрь', 'Nov'),
        ('Декабрь', 'Dec')
    ]
    year = [
        ('2016', '2016'),
        ('2017', '2017'),
        ('2018', '2018'),
    ]

    date_year = models.CharField(max_length=5, choices=year, default='2017')
    date_month = models.CharField(max_length=15, choices=month)
    sum = models.IntegerField(verbose_name=(u'Сумма'))
    account = models.ForeignKey(CableTvPouch, null=True)
    comment = models.CharField(max_length=50, blank=True)
    check = models.BooleanField(default=False)

    class Meta():
        unique_together = ('date_year', 'date_month', 'account')

    def __str__(self):
        return str(self.date_year) +'  '+ str(self.date_month) +' | '+ str(self.account)
