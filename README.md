# Food Ordering Platform 🍔

A simple Django web app for ordering food online. Restaurant owners can add meals, customers can browse and order, and admins can manage everything.

## What We Built So Far

### ✅ Done Stuff
- **User System**: People can sign up and log in (works with username or email)
- **Restaurant Management**: Restaurant owners can add meals, edit their info, and see orders
- **Customer Features**: Browse meals, add to cart, checkout
- **Admin Dashboard**: Simple admin panel to see what's happening
- **Database**: MySQL database with all the tables we need
- **Frontend**: Clean, responsive design that works on phones and computers

### 🔄 Still Working On
- **Cart Updates**: Making the cart update without refreshing the page
- **Order Testing**: Making sure orders work properly
- **API Stuff**: Adding some API endpoints for mobile apps later

## How to Run This Thing

### 1. Get the Code
```bash
git clone [your-repo-url]
cd Food_Ordering_Platform
```

### 2. Set Up Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate it (Linux/Mac)
source venv/bin/activate

# Activate it (Windows)
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Database
- Install MySQL on your computer
- Create a database called `food_ordering_db`
- Update database settings in `Food_Ordering_Platform/settings.py` if needed

### 5. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Admin User
```bash
python manage.py createsuperuser
```

### 7. Start the Server
```bash
python manage.py runserver
```

### 8. Open Your Browser
Go to `http://127.0.0.1:8000`

## What You Can Do

### As a Customer
1. Sign up for an account
2. Browse available meals
3. Add meals to your cart
4. Checkout and place orders

### As a Restaurant Owner
1. Apply for business account
2. Add your restaurant info
3. Add meals to your menu
4. See and manage orders
5. Update your restaurant details

### As an Admin
1. See all users and restaurants
2. Manage the platform
3. View statistics and reports

## File Structure
```
Food_Ordering_Platform/
├── users/           # User accounts and authentication
├── restaurants/     # Restaurant management
├── meals/          # Meal listings and details
├── orders/         # Order processing
├── static/         # CSS, JS, images
└── templates/      # HTML templates
```

## Tech Stuff We Used
- **Django 5.2.6** - Web framework
- **MySQL** - Database
- **Bootstrap 5** - Frontend styling
- **Python 3.12** - Programming language

## Common Issues

**Database Connection Error?**
- Make sure MySQL is running
- Check your database settings in `settings.py`

**Can't See Images?**
- Make sure you ran migrations after adding the image field
- Check that `MEDIA_URL` and `MEDIA_ROOT` are set in settings

**Login Not Working?**
- Try both username and email
- Make sure you created a user account first

## Next Steps
- Finish cart AJAX updates
- Test order placement thoroughly
- Add more admin features
- Maybe deploy to AWS later

## Contact
If something breaks, check the terminal for error messages. Most issues are easy to fix!

---
*Built with Django and a lot of coffee ☕*
