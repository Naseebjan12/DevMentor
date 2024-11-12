from django.shortcuts import render , redirect
from django.contrib import messages # This library is used for displaying the message
from .models import Users # this line simply import the User model
import google.generativeai as genai # Import google generative ai model
import os  # for accessing the api key from the environment variables
import random  # this modeul is used to generate a six digit random  number
from django.core.mail import send_mail  # this module is used for sending emails
import re
from .models import Users , History
import logging

logging.basicConfig(filename='info.log',level=logging.INFO,format=' %(message)s - %(asctime)s - %(levelname)s  ')
# main page view
def index(request):
    return render(request,'index.html')


# use cases view

def usecase(request):
    return render(request,'usecase.html')

# register view
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            # check if user is register or not
            if Users.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
                return redirect('register')
            elif Users.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists')
                return redirect('register')
            else:
                
                # Generate a verification code
                code = generate_six_digit_random()
                
                # Create user with verification code and set is_verified to False
                user = Users.objects.create(
                    username=username,
                    email=email,
                    password=password,
                    verification_code=code,
                    is_verified=False
                )
                
                logging.info(msg=f' user {username} is registered with email {email} successfully...')
                
                     #   Send welcome email 
                try:
                
                    
                    send_welcome_email(user.username,user.email,code)
                    messages.success(request,'User Created Successfully Check your email for the verification code 📩')
                    logging.info(f'Verification email send to {email}')
                    
                    
                except:
                    messages.error(request, 'Failed to send email.')
                    logging.info(f'Failed to send email to {email}')
                user.save()
                
           
                logging.info(f'varifying the email {email}')
                return redirect('verify_email')
        else:
            messages.error(request,'Password do not match')
            return render(request,'register.html')
    return render(request,'register.html')
    
    
# contact View
def contact(request):
    return render(request,'contact.html')



   
def login(request):
     # Check if the request method is POST (form submission)
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        # Authenticate the user (manual authentication)
        user = Users.objects.filter(username=username, password=password).first()
        
        if not user:
            # If no matching user found, show an error message
            messages.error(request, 'Invalid Credentials')
            
            return redirect('login')
        else:
            # Login successful, store the username in session variables
            request.session['username'] = user.username
            request.session['email'] = user.email
            request.session['password'] = user.password  # Optionally store the user ID
            messages.success(request,'User Login Sucessfully')
            logging.info(f'{user } logging successfully...')
            # Redirect to bot page after login
            return redirect('bot')

    # If the method is not POST (GET), just render the login page
    else:
        return render(request, 'login.html')


# function to send email on registration
def send_welcome_email(name , email,code):
    subject = f'Welcome {name} to DevMentor!'
    message = f"""Thank you for registering! We're excited to have you with us. Your verification code is:  {code}. Please use it to complete your registration. """
    from_email = 'genaiapp123@gmail.com'  # Your email address
    recipient =[email]
    send_mail(subject, message, from_email, recipient)






def gemini_response(command):
    """
    Install the Google AI Python SDK

    $ pip install google-generativeai
    """

    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

    # Create the model
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 1000,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
        system_instruction=(
            "The application serves as a chatbot that exclusively provides information, answers, and insights related to computer science topics. It processes user queries and delivers responses based on the most relevant data available in the field of computer science.if the user ask about a programm donot give comments in the code."
        )
    )

    chat_session = model.start_chat(history=[])

    # Get the response from the model
    response = chat_session.send_message(command)
    content = response.text

    # Remove language keywords like `cpp`, `python`, `java`, etc.
    cleaned_content = re.sub(r'\b(cpp|python|java|js|html|css|csharp|ruby|go|swift|kotlin)\b', '', content)

    # Clean up the content by removing extra characters
    cleaned_content = cleaned_content.replace('*', '').replace('`', '').strip()

    return cleaned_content



def bot(request):
    if 'username' not in request.session:
        return redirect('login')

    user_message = None
    bot_response = None
    user_initials = request.session['username'][:2]
    user = Users.objects.get(email=request.session['email'])

    if request.method == 'POST':
        try:
            # Get the user message from the form
            user_message = request.POST['command']
            
            # Get the bot response (assuming gemini_response is defined)
            bot_response = gemini_response(user_message)

           

            # Save the chat history to the database
            History.objects.create(
                user=user,
                user_messages=user_message,
                bot_messages=bot_response
            )
            # retrieve the data from the history model
            chat_history = History.objects.filter(user=user)

            return render(request, 'bot.html', {
                'user_message': user_message,
                'bot_response': bot_response,
                'name': user_initials,
                'chat_history':chat_history
                
            })
        except Exception as e:
            chat_history = History.objects.filter(user=user)
            
            logging.error(f"Error in bot view: {e}")
            bot_response = "There was an error processing your request."
            return render(request, 'bot.html', {
                'user_message': user_message,
                'bot_response': bot_response,
                'name': user_initials,
                'chat_history':chat_history
            
            })
    user = Users.objects.get(email=request.session['email'])
    chat_history = History.objects.filter(user=user)
    return render(request, 'bot.html', {
        'user_message': user_message,
        'bot_response': bot_response,
        'name': user_initials,
        'chat_history':chat_history
    })

# def bot(request):
#     # Check if the user is logged in by checking the session for 'username'
#     if 'username' not in request.session:
#         # If the username is not in the session, redirect to the login page
#         return redirect('login')  # Make sure the 'login' URL name is correct for your login page

#     user_message = None
#     bot_response = None

#     # Retrieve the first two characters of the username from the session
#     user_initials = request.session['username'][:2]

#     if request.method == 'POST':
#         try:
#             # Get the command sent by the user
#             command = request.POST['command']
#             user_message = command
            
#             # Call gemini_response to get the bot's response
#             bot_res = gemini_response(command)
#             bot_response = bot_res    
#             # adding chat history
#             # history=History.objects.create(
#             #     username=request.session['email'],
#             #     user_messages=user_message,
#             #     bot_messages=bot_response   
#             # )
#             # history.save()
            
            
            
#             # Render the bot page with user message and bot response
#             return render(request, 'bot.html', {
                
#                 'user_message': user_message,
#                 'bot_response': bot_response,
#                 'name': user_initials  # Pass the initials to the template
#             })
#         except Exception as e:
#             logging.info(msg=e)
#             # Handle any errors (e.g., API failure)
#             bot_response = "There was an error processing your request."
#             return render(request, 'bot.html', {
#                 'user_message': user_message,
#                 'bot_response': bot_response,
#                 'name': user_initials
#             })
    
#     # If no POST request, simply load the page
#     return render(request, 'bot.html', {
#         'user_message': user_message,
#         'bot_response': bot_response,
#         'name': user_initials  # Pass the initials to the template
#     })

        
# fuction for new chat
def new_chat(request):
    return render(request,'bot.html')



# function to generate six digit random number 


def generate_six_digit_random():
    logging.info('Code Generated successfully... ')
    return random.randint(100000, 999999)





# functio to varify the email
def verify_email(request):
    if request.method == 'POST':
        email = request.POST['email']
        verification_code = request.POST['verification_code']
        
        try:
            user = Users.objects.get(email=email, verification_code=verification_code)
            if user:
                user.is_verified = True  # Mark the user as verified
                user.verification_code = None  # Clear the verification code
                user.save()
                logging.info(f' {user} verified Successfully...')
                messages.success(request, 'Email verified successfully! You can now log in.')
                return redirect('login')
        except Users.DoesNotExist:
            messages.error(request, 'Invalid verification code or email.')
            logging.info(f'{user} Verification failed')
            return redirect('verify_email')
   
    return render(request, 'verify_email.html')
    


def logout(request):
    logging.info(f'Log out Complete...')
    
    return render(request,'login.html')