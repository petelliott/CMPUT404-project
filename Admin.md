# PolarBear Admin documentation

## In grafic interface

### Log in
Login in from the URL: https://cmput404w20t06.herokuapp.com/admin
It will automatically redirect to Amdin Dashboard page.

### Authenticate new sign up auther:

1. Go to Amdin Dashboard page
2. Click USERS under AUTHENTICATION AND AUTHORIZATION
3. Click NO under BY ACTIVE block in the fliter on the right
4. Click any auther name and go into auther information page
5. Tick ACTIVE under PERMISSIONS block
6. Click SAVE BUTTON at the bottom left corner of the page.

### Manage auther:

Add: 
1. Go to Amdin Dashboard page.
2. Click add buttion after AUTHORS tag under USERS blog.

Modify: 
1. Go to Amdin Dashboard page. 
2. Click AUTHORS tag under USERS blog.
3. Click any authors that need to manipulate, fliters are provided on the right.
4. Modify the friend list to current author or the user that links to the author.
5. Click SAVE BUTTON at the bottom left corner of the page.

Delete:
1. Go to Amdin Dashboard page. 
2. Click AUTHORS tag under USERS blog
3. Tick any users that need to be deleted, fliters are provided on the right.
4. Choose Delete select author in the action fliter and click go button.
5. Click Yes to save.
6. Go to Amdin Dashboard page.
7. Click USERS tag under AUTHENTICATION AND AUTHORIZATION blog.
8. Click any auther name and go into auther information page, fliters are provided on the right.
9. Tick ACTIVE under PERMISSIONS block
10. Click SAVE BUTTON at the bottom left corner of the page.

### Manage node:

Add: 
1. Go to Amdin Dashboard page.
2. Click add buttion after node tag under USERS blog.

(Upcoming soon.....)

## In testcase for code: 

u = User.objects.get(username='author')

        u.is_active = True
        
        u.save()
