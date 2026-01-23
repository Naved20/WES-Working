"""Verify that the migration was successful"""
from app import app, db
from sqlalchemy import inspect

with app.app_context():
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns('mentee_profile')]
    
    new_cols = ['address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country']
    
    print('\n' + '='*50)
    print('Verifying Migration...')
    print('='*50)
    
    all_exist = True
    for col in new_cols:
        if col in columns:
            print(f'✓ {col} - EXISTS')
        else:
            print(f'✗ {col} - MISSING')
            all_exist = False
    
    print('\n' + '='*50)
    if all_exist:
        print('✅ All columns exist! Migration successful!')
    else:
        print('❌ Some columns are missing!')
    print('='*50)
    print(f'\nTotal columns in mentee_profile: {len(columns)}')
