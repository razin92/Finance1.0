from django.test import TestCase
from calc.models import Transaction
from lib.models import Pouch, Person, Category
from django.db import transaction
from django.contrib.auth.models import User
import random
from django.utils import timezone

class TransactionTestCase(TestCase):
    def create(self):
        name_set = ['One', 'Another', 'Second', 'More one', 'Something', 'Big']
        User.objects.create_superuser('john', 'lennon@thebeatles.com', 'johnpassword')
        for x in range(0, 1):
            rand_name = random.choice(name_set)
            try:
                # Duplicates should be prevented.
                with transaction.atomic():
                    Pouch.objects.create(name=rand_name, type='SUM')
            except:
                pass
            rand_name = random.choice(name_set)
            try:
                # Duplicates should be prevented.
                with transaction.atomic():
                    Person.objects.create(firstname=rand_name)
            except:
                pass
            rand_name = random.choice(name_set)
            try:
                # Duplicates should be prevented.
                with transaction.atomic():
                    Category.objects.create(name=rand_name)
            except:
                pass

        pouch_set = [x for x in Pouch.objects.all()]
        person_set = [x for x in Person.objects.all()]
        category_set = [x for x in Category.objects.all()]

       # print(pouch_set, person_set, category_set)

        for x in range(0, 1000):
            value = random.randint(0, 1)
            pouch_rand = random.choice(pouch_set)
            person_rand = random.choice(person_set)
            category_rand = random.choice(category_set)
            rand = random.choice([True, False])
            rand_one = random.choice([True, False])
            #print(value, pouch_rand, person_rand, category_rand, rand)
            trans = Transaction.objects.create(
                sum_val=1,
                category=category_rand,
                money=pouch_rand,
                who_is=person_rand,
                checking=rand_one,
                typeof=rand,
            )

            pouch = Pouch.objects.get(id=trans.money_id)
            pouch.balance = pouch.starting_balance
            transaction_set = Transaction.objects.filter(money=pouch)

            tester = 0
            for element in transaction_set:
                if element.typeof and element.checking:
                    pouch.balance += element.sum_val
                    tester += element.sum_val
                    #print('%s' % element.sum_val)
                elif element.checking and not element.typeof:
                    pouch.balance -= element.sum_val
                    tester -= element.sum_val
                    #print('- %s' % element.sum_val)
                pouch.save()
                #print(tester)
                #print('-------------------------------------')
        print('#############################################')
        for element in Transaction.objects.all().order_by('money'):
            print('Typeof= %s, Sum_val= %s, Pouch= %s, Checking= %s' % (
            element.typeof, element.sum_val, element.money.name, element.checking))
        print('#############################################')
        for x in Pouch.objects.all():
            print('Pouch %s with balance %s' % (x.name, x.balance))
        print('#############################################')
        print('True, True = %s' % len([x.sum_val for x in Transaction.objects.filter(checking=True, typeof=True)]))
        print('True, False = %s' % len([x.sum_val for x in Transaction.objects.filter(checking=True, typeof=False)]))
        print('False, True = %s' % len([x.sum_val for x in Transaction.objects.filter(checking=False, typeof=True)]))
        print('False, False = %s' % len([x.sum_val for x in Transaction.objects.filter(checking=False, typeof=False)]))