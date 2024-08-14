from flask import Blueprint, render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt
from models import User, Campaign, AdRequest
from forms import SponsorRegistrationForm, InfluencerRegistrationForm, LoginForm, CampaignForm, AdRequestForm, EditAdRequestForm
from services import get_campaigns
from datetime import datetime

main = Blueprint('main', __name__)

@main.route("/")
def home():
    campaigns = get_campaigns()
    return render_template('home.html', campaigns=campaigns)

@main.route("/register/sponsor", methods=['GET', 'POST'])
def register_sponsor():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = SponsorRegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('An account with this email already exists.', 'danger')
            return redirect(url_for('main.register_sponsor'))
        
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=bcrypt.generate_password_hash(form.password.data).decode('utf-8'),
            role='sponsor',
            company_name=form.company_name.data,
            industry=form.industry.data,
            budget=form.budget.data
        )
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('main.login'))
    return render_template('register_sponsor.html', title='Register as Sponsor', form=form)

@main.route("/register/influencer", methods=['GET', 'POST'])
def register_influencer():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = InfluencerRegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('An account with this email already exists.', 'danger')
            return redirect(url_for('main.register_influencer'))
        
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=bcrypt.generate_password_hash(form.password.data).decode('utf-8'),
            role='influencer',
            name=form.name.data,
            category=form.category.data,
            niche=form.niche.data,
            reach=form.reach.data
        )
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('main.login'))
    return render_template('register_influencer.html', title='Register as Influencer', form=form)

@main.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if user.role == 'admin':
                return redirect(next_page) if next_page else redirect(url_for('main.admin_dashboard'))
            elif user.role == 'sponsor':
                return redirect(next_page) if next_page else redirect(url_for('main.sponsor_dashboard'))
            elif user.role == 'influencer':
                return redirect(next_page) if next_page else redirect(url_for('main.influencer_dashboard'))
            else:
                return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@main.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@main.route("/campaign/new", methods=['GET', 'POST'])
@login_required
def new_campaign():
    form = CampaignForm()
    if form.validate_on_submit():
        campaign = Campaign(
            name=form.name.data,
            description=form.description.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            budget=form.budget.data,
            visibility=form.visibility.data,
            user_id=current_user.id
        )
        db.session.add(campaign)
        db.session.commit()
        flash('Your campaign has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_campaign.html', title='New Campaign', form=form, legend='New Campaign')

@main.route("/campaign/<int:campaign_id>")
def campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    return render_template('campaign.html', title=campaign.name, campaign=campaign)

@main.route("/campaign/<int:campaign_id>/update", methods=['GET', 'POST'])
@login_required
def update_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.user_id != current_user.id:
        abort(403)
    form = CampaignForm()
    if form.validate_on_submit():
        try:
            campaign.name = form.name.data
            campaign.description = form.description.data
            campaign.start_date = form.start_date.data
            campaign.end_date = form.end_date.data
            campaign.budget = float(form.budget.data)
            campaign.visibility = form.visibility.data
            db.session.commit()
            flash('Your campaign has been updated!', 'success')
            return redirect(url_for('main.sponsor_dashboard'))
        except ValueError as e:
            flash(f'Error updating campaign: {e}', 'danger')
            return redirect(url_for('main.update_campaign', campaign_id=campaign_id))
    elif request.method == 'GET':
        form.name.data = campaign.name
        form.description.data = campaign.description
        form.start_date.data = campaign.start_date
        form.end_date.data = campaign.end_date
        form.budget.data = campaign.budget
        form.visibility.data = campaign.visibility
    return render_template('create_campaign.html', title='Update Campaign', form=form, legend='Update Campaign')

@main.route("/campaign/<int:campaign_id>/delete", methods=['POST'])
@login_required
def delete_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.user_id != current_user.id:
        flash('You do not have permission to delete this campaign', 'danger')
        return redirect(url_for('main.home'))
    db.session.delete(campaign)
    db.session.commit()
    flash('Your campaign has been deleted!', 'success')
    return redirect(url_for('main.sponsor_dashboard'))

@main.route("/sponsor/dashboard")
@login_required
def sponsor_dashboard():
    if current_user.role != 'sponsor':
        flash('You do not have access to this page.', 'danger')
        return redirect(url_for('main.home'))
    campaigns = Campaign.query.filter_by(user_id=current_user.id).all()
    return render_template('sponsor_dashboard.html', title='Sponsor Dashboard', campaigns=campaigns)

@main.route("/influencer/dashboard")
@login_required
def influencer_dashboard():
    if current_user.role != 'influencer':
        flash('You do not have access to this page.', 'danger')
        return redirect(url_for('main.home'))
    
    ad_requests = AdRequest.query.filter_by(influencer_id=current_user.id).all()
    public_campaigns = Campaign.query.filter_by(visibility='public').all()
    
    return render_template('influencer_dashboard.html', title='Influencer Dashboard', ad_requests=ad_requests, public_campaigns=public_campaigns)

@main.route("/sponsor/influencers")
@login_required
def search_influencers():
    if current_user.role != 'sponsor':
        flash('You do not have access to this page.', 'danger')
        return redirect(url_for('main.home'))
    influencers = User.query.filter_by(role='influencer').all()
    return render_template('search_influencers.html', title='Search Influencers', influencers=influencers)

@main.route("/influencer/campaigns")
@login_required
def search_campaigns():
    if current_user.role != 'influencer':
        flash('You do not have access to this page.', 'danger')
        return redirect(url_for('main.home'))
    public_campaigns = Campaign.query.filter_by(visibility='public').all()
    return render_template('search_campaigns.html', title='Search Campaigns', public_campaigns=public_campaigns)

@main.route("/sponsor/campaign/<int:campaign_id>/request_ad/<int:influencer_id>", methods=['POST'])
@login_required
def request_ad(campaign_id, influencer_id):
    if current_user.role != 'sponsor':
        flash('You do not have access to this page.', 'danger')
        return redirect(url_for('main.home'))
    ad_request = AdRequest(
        campaign_id=campaign_id,
        influencer_id=influencer_id,
        sponsor_id=current_user.id
    )
    db.session.add(ad_request)
    db.session.commit()
    flash('Ad request sent to influencer.', 'success')
    return redirect(url_for('main.sponsor_dashboard'))

@main.route("/influencer/ad_request/<int:ad_request_id>/accept", methods=['POST'])
@login_required
def accept_ad_request(ad_request_id):
    if current_user.role != 'influencer':
        flash('You do not have access to this page.', 'danger')
        return redirect(url_for('main.home'))
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    ad_request.status = 'accepted'
    db.session.commit()
    flash('Ad request accepted.', 'success')
    return redirect(url_for('main.influencer_dashboard'))

@main.route("/influencer/ad_request/<int:ad_request_id>/reject", methods=['POST'])
@login_required
def reject_ad_request(ad_request_id):
    if current_user.role != 'influencer':
        flash('You do not have access to this page.', 'danger')
        return redirect(url_for('main.home'))
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    ad_request.status = 'rejected'
    db.session.commit()
    flash('Ad request rejected.', 'success')
    return redirect(url_for('main.influencer_dashboard'))

@main.route("/influencer/ad_request/<int:ad_request_id>/negotiate", methods=['POST'])
@login_required
def negotiate_ad_request(ad_request_id):
    if current_user.role != 'influencer':
        flash('You do not have access to this page.', 'danger')
        return redirect(url_for('main.home'))
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    form = EditAdRequestForm()
    if form.validate_on_submit():
        ad_request.payment_amount = form.payment_amount.data
        db.session.commit()
        flash('Ad request payment amount updated.', 'success')
        return redirect(url_for('main.influencer_dashboard'))
    return render_template('edit_ad_request.html', title='Negotiate Ad Request', form=form, ad_request=ad_request)

@main.route("/admin")
@login_required
def admin_dashboard():
    if current_user.email != 'admin@example.com':
        flash('You do not have access to this page.', 'danger')
        return redirect(url_for('main.home'))
    users = User.query.all()
    campaigns = Campaign.query.all()
    ad_requests = AdRequest.query.all()
    return render_template('admin_dashboard.html', title='Admin Dashboard', users=users, campaigns=campaigns, ad_requests=ad_requests)

@main.route("/admin/flag_user/<int:user_id>", methods=['POST'])
@login_required
def flag_user(user_id):
    if current_user.email != 'admin@example.com':
        flash('You do not have access to this page.', 'danger')
        return redirect(url_for('main.home'))
    user = User.query.get_or_404(user_id)
    user.flagged = True
    db.session.commit()
    flash('User has been flagged.', 'success')
    return redirect(url_for('main.admin_dashboard'))

@main.route("/admin/flag_campaign/<int:campaign_id>", methods=['POST'])
@login_required
def flag_campaign(campaign_id):
    if current_user.email != 'admin@example.com':
        flash('You do not have access to this page.', 'danger')
        return redirect(url_for('main.home'))
    campaign = Campaign.query.get_or_404(campaign_id)
    campaign.flagged = True
    db.session.commit()
    flash('Campaign has been flagged.', 'success')
    return redirect(url_for('main.admin_dashboard'))

@main.route("/admin/approve_sponsor/<int:sponsor_id>", methods=['POST'])
@login_required
def approve_sponsor(sponsor_id):
    if current_user.email != 'admin@example.com':
        flash('You do not have access to this page.', 'danger')
        return redirect(url_for('main.home'))
    sponsor = User.query.get_or_404(sponsor_id)
    sponsor.approved = True
    db.session.commit()
    flash('Sponsor approved.', 'success')
    return redirect(url_for('main.admin_dashboard'))
