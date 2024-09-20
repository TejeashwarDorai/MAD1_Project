from application.model import *
from flask import Flask, render_template, request, redirect, url_for, flash, session
from application.database import db 
from main import app
from datetime import *
from sqlalchemy import or_, and_

@app.route('/')
def index():
    if 'user' in session and 'role' in session:
        if session['role'] == 'sponsor':
            niche = Niche.query.all()
            sponsor = Sponsors.query.filter_by(username=session['user']).first()
            campaigns =  Campaigns.query.filter(Campaigns.status == 'Open', Campaigns.sponsor_id==sponsor.sponsor_id).all()
            return render_template('index.html', campaigns=campaigns, niches=niche)
        elif session['role'] == 'influencer':
            influencer = Influencers.query.filter_by(username=session['user']).first()
            niche = Niche.query.filter_by(name=influencer.niche).all()
            campaigns = db.session.query(Campaigns).filter(
                        Campaigns.campaign_id.in_(db.session.query(AdRequests.campaign_id).filter(AdRequests.influencer_id == influencer.influencer_id))
                        ).all()
            campaigns_acc = Campaigns.query.filter(Campaigns.status =='Open', Campaigns.niche==niche[0].name).all()
            return render_template('index.html', campaigns=campaigns, campaigns_acc =campaigns_acc, niches=niche, influencer=influencer)
        elif session['role'] == 'admin':
            niche = Niche.query.all()
            campaigns =  Campaigns.query.filter(Campaigns.status == 'Open').all()
            campaigns_inactive =  Campaigns.query.filter(Campaigns.status != 'Open').all()
            return render_template('index.html', campaigns=campaigns, niches=niche, campaigns_inactive=campaigns_inactive)
    else:
        campaigns =Campaigns.query.all()
        return render_template('index.html', campaigns=campaigns)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Enter all the neccessary fields')
            return redirect(url_for('login'))
        
        user = User.query.filter_by(username=username).first()

        if not user:
            flash('User not found')
            return redirect(url_for('login'))
        
        if password != user.password:
            flash('Wrong Credentials. Enter Again')
            return redirect(url_for('login'))
        
        session['user'] = user.username
        session['role'] = user.role
        if user.role == 'sponsor':
            sponsor = Sponsors.query.filter_by(username=session['user']).first()
            session['id'] =  sponsor.sponsor_id
        
        if user.role == 'influencer':
            influencer = Influencers.query.filter_by(username=session['user']).first()
            session['id'] = influencer.influencer_id
        
        flash('Login Successful')
        return redirect(url_for('index'))
    
@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('role', None)
    flash('You\'ve been logged out')
    return redirect(url_for('index'))

@app.route('/register_user', methods=['GET','POST'])
def register_user():
    if request.method == 'GET':
        return render_template('register_user.html')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        email = request.form['email']
        address = request.form['address']
        role = request.form['role']
        mobile_no = request.form['mobile_no']

        if len(password)<4:
            flash('Length of password is less than 8')
            return redirect(url_for('register_user'))
        
        if password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('register_user'))
        
        check_user = User.query.filter_by(username=username).first()
        if check_user:
            flash('Username already in use.')
            return redirect(url_for('register_user'))
        
        check_email = User.query.filter_by(email=email).first()
        if check_email:
            flash('Email-already linked with some other account')
            return redirect(url_for('register_user'))
        
        check_mobile_no = User.query.filter_by(mobile_no=mobile_no).first()
        if check_mobile_no:
            flash('Mobile Number-already linked with some other account')
            return redirect(url_for('register_user'))
        
        new_user = User(username=username, password=password, role=role, email=email, address=address, mobile_no=mobile_no)
        session['user'] = new_user.username
        db.session.add(new_user)
        db.session.commit()
        if role=='sponsor':
            flash('Proceeding forward with Sponsor Details...')
            return redirect(url_for('register_sponsor'))
        
        if role=='influencer':
            flash('Proceeding forward with Influencer Details...')
            return redirect(url_for('register_influencer'))

@app.route('/register_sponsor', methods=['GET','POST'])
def register_sponsor():
    if request.method == 'GET':
        category_sponsors = Category_sponsors.query.all()
        return render_template('register_sponsor.html',category_sponsors=category_sponsors)
    
    if request.method == 'POST':
        try: 
            name = request.form['sponsor_name']
            category_name = request.form['sponsor_category']
            budget = request.form['budget']

            add_sponsor = Sponsors.query.filter_by(username=session['user']).first()
            if add_sponsor:
                flash('User already registered as a sponsor')
                return redirect(url_for('register_user'))

            add_sponsor = Sponsors(username=session['user'], sponsor_name = name, category_sponsor = category_name, budget = budget)
            
            db.session.add(add_sponsor)
            db.session.commit()
            session.pop('user', None)
            flash('Sponsor Registered Successfully')
            return redirect(url_for('index'))
        except:
            del_user = User.query.filter_by(username=session['user']).first()
            db.session.delete(del_user) 
            db.session.commit()
            session.pop('user', None)
            flash('Error in registration')
            return redirect(url_for('index'))


    
@app.route('/register_influencer', methods=['GET','POST'])
def register_influencer():
    if request.method == 'GET':
        category_influencers = Category_influencers.query.all()
        niche = Niche.query.all()
        return render_template('register_influencer.html',category_influencers=category_influencers, niche=niche)
    
    if request.method == 'POST':
        try:
            name = request.form['influencer_name']
            category_name = request.form['influencer_category']
            niche = request.form['niche']
            reach = request.form['reach']
            earnings=0
            
            add_influencer = Influencers.query.filter_by(username=session['user']).first()
            if add_influencer:
                flash('User already registered as a influencer')
                return redirect(url_for('register_user'))

            add_influencer = Influencers(username=session['user'], influencer_name = name, category_influencer = category_name, reach = reach, niche = niche, earnings=earnings)

            db.session.add(add_influencer)
            db.session.commit()
            session.pop('user', None)
            flash('Influencer Registered Successfully')
            return redirect(url_for('index'))
        
        except:
            del_user = User.query.filter_by(username=session['user']).first()
            db.session.delete(del_user) 
            db.session.commit()
            session.pop('user', None)
            flash('Error in registration')
            return redirect(url_for('index'))

@app.route('/add_category_sponsor', methods=['GET','POST'])
def add_category_sponsor():
    if request.method == 'GET':
        return render_template('add_category_sponsor.html')
    
    if request.method == 'POST':
        name = request.form['category_name']
        description = request.form['description']
        
        category_sponsor=Category_sponsors.query.filter_by(name=name).first()
        if category_sponsor:
            flash('Category of Sponsor already exists')
            return redirect(url_for('add_category_sponsor'))
        
        if session['role'] == 'admin':
            category_sponsor=Category_sponsors(name=name, description=description)
            db.session.add(category_sponsor)
            db.session.commit()
            flash('Sponsor Category added successfully')
            return redirect(url_for('index'))
        
        else:
            flash('You are not authorized to perform this operation')
            return redirect(url_for('index'))
        
@app.route('/add_niche', methods=['GET','POST'])
def add_niche():
    if request.method == 'GET':
        return render_template('add_niche.html')
    
    if request.method == 'POST':
        name = request.form['niche_name']
        description = request.form['description']
        
        niche=Niche.query.filter_by(name=name).first()
        if niche:
            flash('Niche already exists')
            return redirect(url_for('add_niche'))
        
        if session['role'] == 'admin':
            niche=Niche(name=name, description=description)
            db.session.add(niche)
            db.session.commit()
            flash('Niche added successfully')
            return redirect(url_for('index'))
        
        else:
            flash('You are not authorized to perform this operation')
            return redirect(url_for('index'))
        
@app.route('/add_category_influencer', methods=['GET','POST'])
def add_category_influencer():
    if request.method == 'GET':
        return render_template('add_category_influencer.html')
    
    if request.method == 'POST':
        name = request.form['category_name']
        description = request.form['description']
        
        category_influencer=Category_influencers.query.filter_by(name=name).first()
        if category_influencer:
            flash('Category of Influencer already exists')
            return redirect(url_for('add_category_influencer'))
        
        if session['role'] == 'admin':
            category_influencer=Category_influencers(name=name, description=description)
            db.session.add(category_influencer)
            db.session.commit()
            flash('Influencer Category added successfully')
            return redirect(url_for('index'))
        
        else:
            flash('You are not authorized to perform this operation')
            return redirect(url_for('index'))

@app.route('/add_campaign', methods=['GET','POST'])
def add_campaign():
    if request.method == 'GET':
        niche = Niche.query.all()
        return render_template('add_campaign.html', niche=niche)
    
    if request.method == 'POST':
        name = request.form['campaign_name']
        description = request.form['description']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        budget = request.form['budget']
        visibility = request.form['visibility']
        niche = request.form['niche']

        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date,'%Y-%m-%d')

        if start_date > end_date:
            flash('Invalid Start and End date Combination')
            niche = Niche.query.all()
            return render_template('add_campaign.html', niche=niche)

        if session['role'] == 'sponsor':
            add_campaign = Campaigns.query.filter_by(campaign_name=name).first()
            if add_campaign:
                flash('Campaign already exists')
                return redirect(url_for('add_campaign'))
            
            sponsor = Sponsors.query.filter_by(username=session['user']).first()
            
            add_campaign = Campaigns(campaign_name=name,
                                     description=description,
                                     start_date=start_date,
                                     end_date=end_date,
                                     sponsor_id=sponsor.sponsor_id,
                                     budget=budget,
                                     status='Open',
                                     visibility = visibility,
                                     niche=niche
                                     )
            db.session.add(add_campaign)
            db.session.commit()
            flash('Campaign Added Successfully')
            return redirect(url_for('index'))

@app.route('/edit_campaign/<int:id>', methods=['GET','POST'])
def edit_campaign(id):
    if request.method == 'GET':
        campaign = Campaigns.query.filter_by(campaign_id=id).first()
        niche = Niche.query.all()
        return render_template('edit_campaign.html', campaign=campaign, niche=niche)
    
    if request.method == 'POST':
        campaign_edit = Campaigns.query.filter_by(campaign_id=id).first()
        description = request.form['description']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        budget = request.form['budget']
        visibility = request.form['visibility']
        niche = request.form['niche']

        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date,'%Y-%m-%d')

        if start_date > end_date:
            flash('Invalid Start and End date Combination')
            niche = Niche.query.all()
            return render_template('add_campaign.html', niche=niche)

        if description:
            campaign_edit.description=description
        if budget:
            campaign_edit.budget=budget
        if visibility:
            campaign_edit.visibility=visibility
        if start_date:
            campaign_edit.start_date=start_date
        if end_date:
            campaign_edit.end_date=end_date

        db.session.commit()
        flash('Campaign Added Successfully')
        return redirect(url_for('index'))
        
@app.route('/delete_campaign/<int:id>', methods=['POST','GET'])
def delete_campaign(id):
    campaign_deleted=Campaigns.query.filter_by(campaign_id=id).first()
    campaign_deleted.status='Deleted'
    db.session.commit()
    flash('Campaign Deleted')
    return redirect(url_for('index'))

@app.route('/close_campaign/<int:id>', methods=['POST','GET'])
def close_campaign(id):
    campaign_deleted=Campaigns.query.filter_by(campaign_id=id).first()
    campaign_deleted.status='Closed'
    db.session.commit()
    flash('Campaign Deleted')
    return redirect(url_for('index'))
       
@app.route('/add_ad_request/<int:id>', methods=['POST','GET'])
def add_ad_request(id):

    if session['role'] != 'sponsor':
        flash('You are not authorized to add an ad request')
        return redirect(url_for('index'))

    if request.method == 'GET':
        influencers = Influencers.query.all()
        return render_template('add_ad_request.html', campaign_id=id, influencers=influencers)
    
    if request.method == 'POST':
        name = request.form['ad_name']
        description = request.form['description']
        payment_amount = request.form['payment_amount']
        campaign_id = id
        influencer_id = request.form['influencer_id']
        requirements = request.form['requirements']
        payment_amount = request.form['payment_amount']
        start_date  = request.form['start_date']
        end_date = request.form['end_date']
        target_reach = request.form['target_reach']

        end_date = datetime.strptime(end_date, '%Y-%m-%d')

        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')

        if not start_date:
            start_date = datetime.today()

        if not name or not description or not payment_amount or not influencer_id or not requirements or not target_reach:
            flash('Enter all the neccessary fields')
            return redirect(url_for('add_ad_request'))
        
        if session['role'] == 'sponsor':
            add_ad_request = AdRequests.query.filter_by(ad_name=name).first()
            if add_ad_request:
                flash('Ad Request with given name already exists')
                influencers = Influencers.query.all()
                return render_template('add_ad_request.html', campaign_id=id, influencers=influencers)
            
            if start_date > end_date:
                flash('Invalid Start and End date Combination')
                influencers = Influencers.query.all()
                return render_template('add_ad_request.html', campaign_id=id, influencers=influencers)
            
            add_ad_request = AdRequests(ad_name=name,
                                        description=description,
                                        campaign_id=campaign_id,
                                        influencer_id=influencer_id,
                                        requirements=requirements,
                                        payment_amount=payment_amount,
                                        status='Open',
                                        start_date = start_date,
                                        end_date = end_date,
                                        target_reach = target_reach,
                                        )
            db.session.add(add_ad_request)
            db.session.commit()
            flash('Ad Request added successfully')
            return redirect(url_for('index'))

@app.route('/edit_ad_request/<int:id>', methods=['POST','GET'])
def edit_ad_request(id):

    if session['role'] != 'sponsor':
        flash('You are not authorized to edit an ad request')
        return redirect(url_for('index'))

    if request.method == 'GET':
        ad_request_edit = AdRequests.query.get(id)
        influencers = Influencers.query.all()
        if not ad_request_edit: 
            flash('Ad Request not found')
            return redirect(url_for('index'))
        return render_template('edit_ad_request.html', ad_request=ad_request_edit, influencers=influencers)
    
    if request.method == 'POST':
        ad_request_edit = AdRequests.query.filter_by(id=id).first()
        description = request.form['description']
        influencer_id = request.form['influencer_id']
        requirements = request.form['requirements']
        payment_amount = request.form['payment_amount']
        start_date  = request.form['start_date']
        end_date = request.form['end_date']
        target_reach = request.form['target_reach']

        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
            
        if start_date > end_date:
            flash('Invalid Start and End date Combination')
            influencers = Influencers.query.all()
            return render_template('edit_ad_request.html',  ad_request=ad_request_edit, influencers=influencers)

        if description:
            ad_request_edit.description=description
        if payment_amount:
            ad_request_edit.payment_amount=payment_amount
        if influencer_id:
            ad_request_edit.influencer_id=influencer_id
        if requirements:
            ad_request_edit.requirements=requirements
        if start_date:
            ad_request_edit.start_date=start_date
        if end_date:
            ad_request_edit.end_date=end_date
        if target_reach:
            ad_request_edit.target_reach=target_reach
            
        db.session.commit()
        flash('Ad Request updated successfully')
        return redirect(url_for('index'))
            
@app.route('/view_ad_request/<int:id>', methods=['POST','GET'])
def view_ad_request(id):
    campaign = Campaigns.query.filter_by(campaign_id=id).first()
    if 'role' in session and session['role']=='admin':
        ad_requests = AdRequests.query.filter_by(campaign_id=id).all()
        sponsor = Sponsors.query.filter_by(sponsor_id = campaign.sponsor_id ).first()
        return render_template('view_ad_request.html',ad_requests=ad_requests, sponsor=sponsor)  
    if 'role' in session and session['role']=='sponsor':
        ad_requests = AdRequests.query.filter_by(campaign_id=id).all()
        sponsor = Sponsors.query.filter_by(sponsor_id = campaign.sponsor_id ).first()
        return render_template('view_ad_request.html',ad_requests=ad_requests, sponsor=sponsor)
    if 'role' in session and session['role']=='influencer':
        influencer = Influencers.query.filter_by(username=session['user']).first()
        ad_requests = AdRequests.query.filter_by(influencer_id=influencer.influencer_id, campaign_id=id).all()
        sponsor = Sponsors.query.filter_by(sponsor_id = campaign.sponsor_id ).first()
        return render_template('view_ad_request.html', ad_requests=ad_requests, influencer = influencer, sponsor=sponsor)
    
@app.route('/view_accepted_ad_request/<int:id>', methods=['POST','GET'])
def view_accepted_ad_request(id):
    campaign = Campaigns.query.filter_by(campaign_id=id).first()
    if 'role' in session and session['role']=='influencer':
        influencer = Influencers.query.filter_by(username=session['user']).first()
        ad_requests = AdRequests.query.filter_by(influencer_id=influencer.influencer_id, campaign_id=id, status='Accepted').all()
        sponsor = Sponsors.query.filter_by(sponsor_id = campaign.sponsor_id ).first()
        return render_template('view_ad_request.html', ad_requests=ad_requests, influencer = influencer, sponsor=sponsor)

@app.route('/view_available_ad_request/<int:id>', methods=['POST','GET'])
def view_available_ad_request(id):
    campaign = Campaigns.query.filter_by(campaign_id=id).first()
    if 'role' in session and session['role']=='influencer':
        influencer = Influencers.query.filter_by(username=session['user']).first()
        ad_requests = AdRequests.query.filter_by(influencer_id=influencer.influencer_id, campaign_id=id, status='Open').all()
        sponsor = Sponsors.query.filter_by(sponsor_id = campaign.sponsor_id ).first()
        return render_template('view_available_ad_request.html', ad_requests=ad_requests, influencer = influencer, sponsor=sponsor)

@app.route('/view_completed_ad_request/<int:id>', methods=['POST','GET'])
def view_completed_ad_request(id):
    campaign = Campaigns.query.filter_by(campaign_id=id).first()
    if 'role' in session and session['role']=='sponsor':
        ad_requests = AdRequests.query.filter_by(campaign_id=id, status='Completed').all()
        sponsor = Sponsors.query.filter_by(sponsor_id = campaign.sponsor_id ).first()
        return render_template('view_completed_ad_request.html', ad_requests=ad_requests, sponsor=sponsor)

    if 'role' in session and session['role']=='influencer':
        influencer = Influencers.query.filter_by(username=session['user']).first()
        ad_requests = AdRequests.query.filter(and_(AdRequests.influencer_id==influencer.influencer_id, AdRequests.campaign_id==id, or_(AdRequests.status=='Completed', AdRequests.status=='Approved', AdRequests.status=='Disapproved'))).all()
        sponsor = Sponsors.query.filter_by(sponsor_id = campaign.sponsor_id ).first()
        return render_template('view_completed_ad_request.html', ad_requests=ad_requests, sponsor=sponsor)


@app.route('/delete_ad_request/<int:id>', methods=['POST','GET'])
def delete_ad_request(id):
    if 'role' in session and (session['role']=='admin' or session['role']=='sponsor'):
        ad_request_delete = AdRequests.query.filter_by(id=id).first()
        ad_request_delete.status='Deleted'
        db.session.commit()
        flash('Ad Request Deleted')
        return redirect(url_for('index'))
    
@app.route('/accept_ad_request/<int:id>', methods=['POST','GET'])
def accept_ad_request(id):
    ad_request_accept = AdRequests.query.filter_by(id=id).first()
    ad_request_accept.status='Accepted'
    db.session.commit()
    flash('Ad Request Accepted')
    return redirect(url_for('index'))

@app.route('/reject_ad_request/<int:id>', methods=['POST','GET'])
def reject_ad_request(id):
    ad_request_accept = AdRequests.query.filter_by(id=id).first()
    ad_request_accept.status='Rejected'
    db.session.commit()
    flash('Ad Request Rejected')
    return redirect(url_for('index'))

@app.route('/reject_ad_request_now/<int:id>', methods=['POST','GET'])
def reject_ad_request_now(id):
    ad_request_accept = AdRequests.query.filter_by(id=id).first()
    ad_request_accept.status='Rejected later'
    db.session.commit()
    flash('Ad Request Rejected')
    return redirect(url_for('index'))

@app.route('/completed_ad_request/<int:id>', methods=['POST','GET'])
def completed_ad_request(id):
    ad_request_accept = AdRequests.query.filter_by(id=id).first()
    ad_request_accept.status='Completed'
    flash('Ad Request marked as complete')
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/approve_ad_request/<int:id>', methods=['POST','GET'])
def approve_ad_request(id):
    ad_request_accept = AdRequests.query.filter_by(id=id).first()
    influencer_id = ad_request_accept.influencer_id
    influencer_success = Influencers.query.filter_by(influencer_id=influencer_id).first()
    influencer_success.earnings = influencer_success.earnings + ad_request_accept.payment_amount
    ad_request_accept.status='Approved'
    flash('Ad Request marked as Approved')
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/disapprove_ad_request/<int:id>', methods=['POST','GET'])
def disapprove_ad_request(id):
    ad_request_accept = AdRequests.query.filter_by(id=id).first()
    ad_request_accept.status='Disapproved'
    flash('Ad Request DisApproved')
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/go_back',  methods=['POST', 'GET'])
def go_back():
    return redirect(url_for('index'))

@app.route('/search',methods=['GET','POST'])
def search():
    if request.method == 'POST':
        search = request.form.get('search', None)
        if search:
            flash('Please enter search keyword')
            return redirect(url_for('index'))
        
        campaigns = Campaigns.query.filter(Campaigns.campaign_name.like(f'%{search}%')).all()
        ad_requests = AdRequests.query.filter(AdRequests.ad_name.like(f'%{search}%')).all()
        return render_template('search.html',ad_requests=ad_requests,campaigns=campaigns)


@app.route('/view_statistics',methods=['GET','POST'])
def view_statistics():
      if request.method == 'GET':
        influencers = Influencers.query.all()
        sponsors = Sponsors.query.all()
        ad_requests_all = AdRequests.query.all()
        ad_requests_open = AdRequests.query.filter_by(status='Open').all()
        ad_requests_approved = AdRequests.query.filter_by(status='Approved').all()
        ad_requests_disapproved = AdRequests.query.filter_by(status='Disapproved').all()
        campaigns_all = Campaigns.query.all()
        campaigns_open = Campaigns.query.filter_by(status='Open').all()
        campaigns_closed = Campaigns.query.filter_by(status='Closed').all()
        campaigns_deleted = Campaigns.query.filter_by(status='Deleted').all()

        total_count = len(influencers) + len(sponsors)

        net_worth=0
        for campaign in campaigns_open:
            net_worth = net_worth + campaign.budget
        for campaign in campaigns_closed:
            net_worth = net_worth + campaign.budget

        success_ratio_ads = len(ad_requests_approved)/len(ad_requests_all)
        success_ratio_campaigns = len(campaigns_closed)/len(campaigns_all)
        return render_template('view_statistics.html',
                                influencers=influencers, sponsors=sponsors,
                                ad_requests_all=ad_requests_all, ad_requests_open=ad_requests_open, ad_requests_approved=ad_requests_approved, ad_requests_disapproved=ad_requests_disapproved,
                                campaigns_all=campaigns_all, campaigns_open=campaigns_open,  campaigns_closed= campaigns_closed, campaigns_deleted = campaigns_deleted,
                                total_count=total_count, net_worth=net_worth, success_ratio_ads=success_ratio_ads,success_ratio_campaigns=success_ratio_campaigns
   )
    