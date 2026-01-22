"""
Django Signals for Gamification
Automatically check for badges when activities occur
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PatientSymptomLog
from .gamification_service import GamificationService


@receiver(post_save, sender=PatientSymptomLog)
def check_badges_on_symptom_log(sender, instance, created, **kwargs):
    """Check for badges when a symptom log is created"""
    if created:
        # Award points for logging symptoms
        GamificationService.award_points(
            instance.patient,
            points=10,
            activity_type='symptom_logged',
            description='Logged symptoms'
        )
        
        # Check for badge eligibility
        activity_data = {
            'id': str(instance.id),
            'log_date': instance.log_date.isoformat(),
        }
        GamificationService.check_and_award_badges(
            instance.patient,
            activity_type='symptom_logged',
            activity_data=activity_data
        )
        
        # Check for level up
        GamificationService.check_level_up(instance.patient)

