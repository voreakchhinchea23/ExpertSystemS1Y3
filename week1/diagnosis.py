# covid-19 symptom
has_fever = input('Do you have fever? (yes/no): ').strip().lower() == 'yes'
has_dry_cough = input('Do you have dry cough? (yes/no): ').strip().lower() == 'yes'
has_difficult_breathing = input('Do you have difficult breathing? (yes/no): ').strip().lower() == 'yes'
has_tiredness = input('Do you have tiredness? (yes/no): ').strip().lower() == 'yes'
has_headache = input('Do you have headache? (yes/no): ').strip().lower() == 'yes'

if has_fever and has_dry_cough and has_difficult_breathing and has_tiredness:
    print('\nDiagnosis: You might have COVID-19.')
elif has_fever and has_headache and not has_difficult_breathing:
    print('\nDiagnosis: You might have the flu.')
elif has_headache and not has_fever:
    print('\nDiagnosis: You might have a mild cold or stress-related headache.')
elif has_tiredness and not has_fever and not has_dry_cough:
    print('\nDiagnosis: You might just be tired or need rest.')
else:
    print('\nDiagnosis: Symptoms are unclear. Please monitor your health or consult a doctor.')
