from application.database import db

class User(db.Model):
    username = db.Column(db.String(80), primary_key=True)
    password = db.Column(db.String(40), nullable=False)
    role = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    address = db.Column(db.String(120), nullable=False)
    mobile_no = db.Column(db.String(10), nullable=False, unique=True)

class Category_influencers(db.Model):
    category_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(40), nullable=False)
    description = db.Column(db.String(512), nullable=True)

    influencer = db.relationship('Influencers', backref='category_influencers', lazy=True)

class Influencers(db.Model):
    influencer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), db.ForeignKey('user.username'), nullable=False, unique=True)
    influencer_name = db.Column(db.String(80), nullable=False)
    category_influencer = db.Column(db.String(40), db.ForeignKey('category_influencers.name'), nullable=False)
    niche = db.Column(db.String(200),  db.ForeignKey('niche.name'), nullable=False)
    reach = db.Column(db.Integer, nullable=False)
    earnings = db.Column(db.Integer, nullable=True)

class Category_sponsors(db.Model):
    category_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(40), nullable=False)
    description = db.Column(db.String(512), nullable=True)

    sponsor = db.relationship('Sponsors', backref='category_sponsors', lazy=True)

class Sponsors(db.Model):
    sponsor_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), db.ForeignKey('user.username'), nullable=False, unique=True)
    sponsor_name = db.Column(db.String(80), nullable=False)
    category_sponsor = db.Column(db.String(40), db.ForeignKey('category_sponsors.name'), nullable=False)
    budget = db.Column(db.Integer, nullable=False)

    campaign = db.relationship('Campaigns', backref='Sponsors', lazy=True)

class Campaigns(db.Model):
    campaign_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    campaign_name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(512), nullable=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsors.sponsor_id'), nullable=False)
    budget = db.Column(db.Integer, nullable=False)
    niche = db.Column(db.String(200), nullable=True)
    visibility = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False)

    ad = db.relationship('AdRequests', backref='Campaigns', lazy=True)

class AdRequests(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ad_name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(512), nullable=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.campaign_id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencers.influencer_id'), nullable=True)
    messages = db.Column(db.String(80), nullable=True)
    requirements = db.Column(db.String(255), nullable=False)
    payment_amount = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    target_reach = db.Column(db.Integer, nullable=False)

class Niche(db.Model):
    niche_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(40), nullable=False)
    description = db.Column(db.String(512), nullable=True)  
