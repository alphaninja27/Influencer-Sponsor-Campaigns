from celery import Celery
from flask_mail import Mail, Message
from app import app, db
from models import User, Campaign, AdRequest
import csv
import os

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    return celery

celery = make_celery(app)

# Initialize Flask-Mail
mail = Mail(app)

@celery.task
def send_daily_reminder():
    with app.app_context():
        # Get all influencers
        influencers = User.query.filter_by(role='influencer').all()
        for influencer in influencers:
            # Check for pending ad requests
            pending_requests = AdRequest.query.filter_by(influencer_id=influencer.id, status='Pending').count()
            if pending_requests > 0:
                # Send reminder email
                msg = Message('Daily Reminder', 
                              sender='noreply@example.com', 
                              recipients=[influencer.email])
                msg.body = f'You have {pending_requests} pending ad requests. Please review them.'
                mail.send(msg)

@celery.task
def generate_monthly_report():
    with app.app_context():
        # Get all sponsors
        sponsors = User.query.filter_by(role='sponsor').all()
        for sponsor in sponsors:
            # Get sponsor's campaigns
            campaigns = Campaign.query.filter_by(user_id=sponsor.id).all()
            report_content = 'Monthly Activity Report\n\n'
            for campaign in campaigns:
                report_content += f'Campaign: {campaign.name}\n'
                ad_requests = AdRequest.query.filter_by(campaign_id=campaign.id).all()
                for ad_request in ad_requests:
                    report_content += f'  - Ad Request: {ad_request.id}, Status: {ad_request.status}\n'
                report_content += '\n'
            # Send report email
            msg = Message('Monthly Activity Report', 
                          sender='noreply@example.com', 
                          recipients=[sponsor.email])
            msg.body = report_content
            mail.send(msg)

@celery.task
def export_campaigns_to_csv(sponsor_id):
    with app.app_context():
        sponsor = User.query.get(sponsor_id)
        campaigns = Campaign.query.filter_by(user_id=sponsor.id).all()
        
        # Create CSV content
        csv_content = 'Campaign ID,Name,Description,Start Date,End Date,Budget,Visibility,Goals\n'
        for campaign in campaigns:
            csv_content += f'{campaign.id},{campaign.name},{campaign.description},{campaign.start_date},{campaign.end_date},{campaign.budget},{campaign.visibility},{campaign.goals}\n'
        
        # Save CSV to file
        csv_filename = f'{sponsor.username}_campaigns.csv'
        with open(csv_filename, 'w') as csv_file:
            csv_file.write(csv_content)
        
        # Send CSV file via email
        msg = Message('Your Campaigns CSV Export', 
                      sender='noreply@example.com', 
                      recipients=[sponsor.email])
        with app.open_resource(csv_filename) as fp:
            msg.attach(csv_filename, 'text/csv', fp.read())
        mail.send(msg)
        
        # Delete the CSV file after sending
        os.remove(csv_filename)
