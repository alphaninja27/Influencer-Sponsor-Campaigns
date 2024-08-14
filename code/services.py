from app import redis_store, db
from models import Campaign
import json

def get_campaigns():
    cached_campaigns = redis_store.get('campaigns')
    if cached_campaigns:
        return json.loads(cached_campaigns)

    campaigns = Campaign.query.all()
    campaign_list = [{"id": campaign.id, "name": campaign.name, "description": campaign.description, "start_date": campaign.start_date.strftime('%Y-%m-%d'), "end_date": campaign.end_date.strftime('%Y-%m-%d'), "budget": campaign.budget, "visibility": campaign.visibility} for campaign in campaigns]
    
    redis_store.set('campaigns', json.dumps(campaign_list))
    return campaign_list
