import random
from sqlalchemy.orm import Session
from Models.database import local_session, engine
from Models.model import ecoFacilities, ecoCategories, ecoUser

# Sample data for realistic facilities
facility_names = [
    "Green Energy Solar Farm", "Eco-Friendly Recycling Center", "Sustainable Community Garden", 
    "Wind Power Station", "Organic Waste Composting Facility", "Electric Vehicle Charging Hub",
    "Rainwater Harvesting Center", "Solar Panel Installation Point", "Biodegradable Packaging Plant",
    "Green Building Materials Store", "Renewable Energy Workshop", "Eco-Tourism Center",
    "Sustainable Fashion Boutique", "Green Tech Innovation Lab", "Organic Food Market",
    "Zero Waste Grocery Store", "Environmental Education Center", "Clean Air Monitoring Station",
    "Tree Planting Initiative Hub", "Green Roof Garden", "Sustainable Transport Hub",
    "Eco-Friendly Car Wash", "Renewable Energy Consultation", "Green Living Workshop",
    "Sustainable Agriculture Center", "Environmental Research Facility", "Clean Water Treatment Plant",
    "Green Energy Storage Facility", "Eco-Conscious Co-working Space", "Sustainable Textile Mill"
]

descriptions = [
    "A state-of-the-art facility promoting environmental sustainability and green practices.",
    "Dedicated to reducing carbon footprint through innovative eco-friendly solutions.",
    "Community-focused initiative supporting sustainable living and environmental awareness.",
    "Advanced facility utilizing renewable energy sources for environmental conservation.",
    "Innovative center promoting circular economy and sustainable resource management.",
    "Modern facility equipped with latest green technology and sustainable practices.",
    "Environmental hub dedicated to creating positive impact on local ecosystem.",
    "Sustainable facility supporting community-wide environmental initiatives.",
    "Green technology center focused on renewable energy and environmental protection.",
    "Eco-friendly facility promoting sustainable development and green innovation."
]

uk_towns = [
    "London", "Birmingham", "Manchester", "Liverpool", "Leeds", "Sheffield", "Bristol",
    "Edinburgh", "Glasgow", "Cardiff", "Belfast", "Newcastle", "Nottingham", "Leicester",
    "Southampton", "Portsmouth", "Brighton", "Plymouth", "Reading", "Bolton", "Huddersfield",
    "Preston", "Newport", "Swansea", "Bradford", "Southend", "Oxford", "Cambridge",
    "Ipswich", "Norwich", "Exeter", "Bath", "York", "Chester", "Canterbury", "Salisbury"
]

uk_counties = [
    "Greater London", "West Midlands", "Greater Manchester", "Merseyside", "West Yorkshire",
    "South Yorkshire", "Avon", "Lothian", "Strathclyde", "South Glamorgan", "Antrim",
    "Tyne and Wear", "Nottinghamshire", "Leicestershire", "Hampshire", "East Sussex",
    "Devon", "Berkshire", "Greater Manchester", "Lancashire", "Gwent", "West Glamorgan",
    "Oxfordshire", "Cambridgeshire", "Suffolk", "Norfolk", "Somerset", "North Yorkshire",
    "Cheshire", "Kent", "Wiltshire"
]

street_names = [
    "High Street", "Church Lane", "Main Road", "Victoria Street", "Queen's Road", "King Street",
    "Mill Lane", "School Road", "Park Avenue", "Station Road", "Green Lane", "Oak Avenue",
    "Church Street", "Manor Road", "The Grove", "Springfield Road", "Meadow Lane", "Hill Street",
    "Wood Lane", "River Road", "Garden Street", "Elm Road", "Pine Avenue", "Rose Street"
]

def generate_postcode():
    """Generate a realistic UK postcode"""
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return f"{random.choice(letters)}{random.choice(letters)}{random.randint(1,99)} {random.randint(1,9)}{random.choice(letters)}{random.choice(letters)}"

def populate_facilities():
    db = local_session()
    
    try:
        # Get existing categories and users
        categories = db.query(ecoCategories).all()
        users = db.query(ecoUser).all()
        
        if not categories:
            print("No categories found! Please add categories first.")
            return
            
        if not users:
            print("No users found! Please add users first.")
            return
        
        print(f"Found {len(categories)} categories and {len(users)} users")
        print("Starting to create 500 facilities...")
        
        for i in range(500):
            # Generate facility data
            title = f"{random.choice(facility_names)} {i+1}"
            category_id = random.choice(categories).id
            description = random.choice(descriptions)
            house_number = str(random.randint(1, 999))
            street_name = random.choice(street_names)
            town = random.choice(uk_towns)
            county = random.choice(uk_counties)
            postcode = generate_postcode()e
            contributor_id = random.choice(users).id
            
            # Generate realistic UK coordinates
            # UK roughly: lat 49.9-60.9, lng -8.2-1.8
            lat = round(random.uniform(50.0, 59.0), 6)
            lng = round(random.uniform(-6.0, 2.0), 6)
            
            # Create new facility
            new_facility = ecoFacilities(
                title=title,
                category=category_id,
                description=description,
                houseNumber=house_number,
                streetName=street_name,
                town=town,
                county=county,
                postcode=postcode,
                contributor=contributor_id,
                lat=lat,
                lng=lng
            )
            
            db.add(new_facility)
            
            # Commit every 50 facilities to avoid memory issues
            if (i + 1) % 50 == 0:
                db.commit()
                print(f"Created {i + 1} facilities...")
        
        # Final commit
        db.commit()
        print("Successfully created 500 facilities!")
        
        # Show summary
        total_facilities = db.query(ecoFacilities).count()
        print(f"Total facilities in database: {total_facilities}")
        
    except Exception as e:
        print(f"Error creating facilities: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_facilities() 