# Configuration file for Happy Paws Vet Clinic

# Services offered by the clinic
SERVICES = [
    {
        'title': 'Wellness Checkup',
        'desc': 'Routine physical exam and health check.',
        'price': '₱500'
    },
    {
        'title': 'Vaccination',
        'desc': 'Core vaccines and booster shots.',
        'price': '₱800'
    },
    {
        'title': 'Surgery',
        'desc': 'Minor surgical procedures.',
        'price': '₱3,000'
    },
    {
        'title': 'Deworming',
        'desc': 'Eliminates intestinal worms and parasites.',
        'price': '₱350'
    },
    {
        'title': 'Dental Cleaning',
        'desc': 'Removes tartar and improves oral health.',
        'price': '₱1,200'
    },
    {
        'title': 'Grooming',
        'desc': 'Basic grooming, nail trimming, and bathing.',
        'price': '₱600'
    },
]

# Staff members
STAFF = [
    {
        'name': 'Jan Paul E. De Quiroz', 'role': 'Senior Veterinarian', 'bio': 'Expert in animal health and wellness with years of dedicated service.'
    },

    {
        'name': 'Danniel John Morales', 'role': 'Veterinarian', 'bio': 'Specializes in surgery and compassionate pet care.'
    },

    {
        'name': 'Zuriel Pecadero', 'role': 'Help Desk', 'bio': 'Helps you with your inquiries.'
    },

    {
        'name': 'Kim Tomotorgo', 'role': 'Wellness Veterinarian', 'bio': 'Focused on Wellness Checkups and ensuring pets maintain optimal health.'

    },

    {
        'name': 'Vanessa Ofrancia', 'role': 'Veterinary Nurse', 'bio': 'Specializes in Vaccination and preventive care to keep pets safe from diseases.'
    },

    {
        'name': 'Irish Rocha', 'role': 'Veterinary Surgical Nurse', 'bio': 'Assists in Surgery and post-operative care with precision and compassion.'
    },

    {
        'name': 'Ellemar Pundavela', 'role': 'Preventive Care Specialist', 'bio': 'Specializes in Deworming and preventive pet treatments.'
    },

    {
        'name': 'Ruffaina Hamsain', 'role': 'Dental Care Specialist', 'bio': 'Expert in Dental Cleaning and oral care for pets.'
    },

    {
        'name': 'Rose Ann Tolentino', 'role': 'Grooming Specialist', 'bio': 'Specializes in Grooming and maintaining pet hygiene.'
    }
]

# Service prices mapping for quick lookup (numeric values for calculations)
service_prices = {
    'Wellness Checkup': 500.0,
    'Vaccination': 800.0,
    'Surgery': 3000.0,
    'Deworming': 350.0,
    'Dental Cleaning': 1200.0,
    'Grooming': 600.0
}
