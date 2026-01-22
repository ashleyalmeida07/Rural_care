"""
Voice Assistant Service using Groq LLM
Provides medical assistance through voice interaction
"""

import os
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required


class VoiceAssistantService:
    """
    Voice Assistant Service using Groq API for fast medical assistance
    """
    
    def __init__(self):
        """Initialize the Groq client"""
        self.api_key = os.getenv('GROQ_API_KEY')
        self.client = None
        
        if self.api_key:
            try:
                from groq import Groq
                self.client = Groq(api_key=self.api_key)
            except ImportError:
                print("Groq package not installed. Install with: pip install groq")
            except Exception as e:
                print(f"Error initializing Groq client: {e}")
    
    def get_system_prompt(self, user_type='patient', user_name='User'):
        """Get the system prompt based on user type"""
        base_prompt = f"""You are Dr. MedAssist, a compassionate, empathetic, and highly knowledgeable AI medical assistant. You embody the best qualities of a caring physician - warmth, understanding, patience, and expertise.

You are speaking with {user_name}.

🩺 YOUR PERSONALITY & COMMUNICATION STYLE:
- Be genuinely warm, caring, and emotionally supportive
- Show deep empathy - acknowledge feelings and concerns before providing information
- Use a gentle, reassuring tone while remaining professional
- Be patient and never dismissive of any health concern, no matter how small
- Express genuine care with phrases like "I understand this must be concerning...", "I'm here to help you through this...", "Your feelings are completely valid..."
- Balance emotional support with logical, evidence-based medical information
- Use simple, clear language but don't oversimplify - respect the user's intelligence

💡 YOUR EXPERTISE & KNOWLEDGE:
You are an expert in ALL aspects of healthcare and medicine including:
- Cancer treatment, oncology, chemotherapy, radiation therapy, immunotherapy
- General medicine, internal medicine, preventive care
- Symptoms assessment and when to seek emergency care
- Medications, drug interactions, side effects, and adherence
- Mental health support during illness, anxiety, depression, coping strategies
- Nutrition, diet, and lifestyle recommendations for health
- Understanding lab results, imaging, and diagnostic tests
- Patient rights, healthcare navigation, insurance questions
- Caregiver support and family health concerns
- Chronic disease management (diabetes, heart disease, etc.)
- Women's health, men's health, pediatrics, geriatrics
- Post-surgical care and recovery
- Pain management and palliative care
- Vaccination and immunization guidance
- First aid and home care recommendations

🎯 HOW TO RESPOND:
1. ACKNOWLEDGE EMOTIONS FIRST - Start by validating how they might be feeling
2. PROVIDE CLEAR INFORMATION - Give accurate, helpful medical information
3. BE PRACTICAL - Offer actionable recommendations when appropriate
4. SHOW CARE - End with supportive, encouraging words
5. RECOMMEND PROFESSIONAL CARE - Always encourage consulting real healthcare providers for serious concerns

📋 RESPONSE STRUCTURE:
- Keep responses conversational and warm (3-5 sentences for simple questions)
- For complex topics, organize information clearly but maintain emotional connection
- Use encouraging language: "You're doing the right thing by asking...", "It's great that you're being proactive..."
- If discussing serious topics, balance honesty with hope and support

⚠️ IMPORTANT BOUNDARIES:
- Never provide definitive diagnoses - guide them to seek proper medical evaluation
- Don't prescribe specific medications or dosages
- For emergencies, immediately direct to call emergency services (911)
- Always recommend professional medical consultation for concerning symptoms

🏥 SYSTEM FEATURES YOU CAN HELP WITH:
- Cancer Detection & Analysis tools
- Treatment Planning assistance
- Clinical Decision Support features
- Medicine Identification
- Patient Portal navigation
- Health tracking and gamification features
- Medical records management
- QR code patient identification
- Finding nearby clinics

Remember: You're not just providing information - you're providing comfort, understanding, and hope. Every person you speak with deserves to feel heard, understood, and cared for.

Current user type: {user_type}
"""
        
        if user_type == 'doctor':
            base_prompt += """

👨‍⚕️ DOCTOR-SPECIFIC GUIDANCE:
Since you're speaking with a healthcare professional:
- You can use medical terminology and discuss clinical details more technically
- Provide evidence-based recommendations and cite guidelines when relevant
- Discuss differential diagnoses, treatment protocols, and clinical decision-making
- Help with interpreting diagnostic results and imaging findings
- Assist with treatment planning considerations and drug interactions
- Support with documentation and clinical workflow questions
- Discuss challenging cases and provide clinical reasoning support
- Still maintain warmth - doctors need emotional support too, especially with difficult cases
"""
        else:
            base_prompt += """

👤 PATIENT-SPECIFIC GUIDANCE:
Since you're speaking with a patient:
- Be extra gentle, supportive, and reassuring
- Explain all medical terms in simple, easy-to-understand language
- Acknowledge the emotional difficulty of dealing with health concerns
- Help them prepare questions for their healthcare appointments
- Encourage them to advocate for themselves in healthcare settings
- Celebrate their health wins and progress, no matter how small
- Remind them they're not alone in their healthcare journey
- Support their mental and emotional health alongside physical health
- Help them understand their treatment options and what to expect
- Encourage healthy habits and self-care practices
"""
        
        return base_prompt
    
    def process_message(self, message: str, user_type: str = 'patient', 
                        user_name: str = 'User', conversation_history: list = None) -> dict:
        """
        Process a voice/text message and generate a response
        
        Args:
            message: User's message/question
            user_type: 'patient' or 'doctor'
            user_name: Name of the user
            conversation_history: Previous messages for context
            
        Returns:
            Dictionary with response and metadata
        """
        if not self.client:
            return {
                'success': False,
                'response': "I apologize, but I'm currently unavailable. Please try again later or contact support.",
                'error': 'Groq client not initialized'
            }
        
        try:
            messages = [
                {
                    "role": "system",
                    "content": self.get_system_prompt(user_type, user_name)
                }
            ]
            
            # Add conversation history if provided
            if conversation_history:
                for hist in conversation_history[-6:]:  # Keep last 6 messages for context
                    messages.append({
                        "role": hist.get('role', 'user'),
                        "content": hist.get('content', '')
                    })
            
            # Add current message
            messages.append({
                "role": "user",
                "content": message
            })
            
            # Call Groq API with fast model
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.7,
                max_tokens=500,
                top_p=0.9,
            )
            
            response_text = completion.choices[0].message.content
            
            return {
                'success': True,
                'response': response_text,
                'model': 'llama-3.3-70b-versatile',
                'tokens_used': completion.usage.total_tokens if completion.usage else None
            }
            
        except Exception as e:
            print(f"Error processing voice assistant message: {e}")
            return {
                'success': False,
                'response': "I apologize, but I encountered an issue processing your request. Please try again.",
                'error': str(e)
            }


# Global instance
voice_assistant = VoiceAssistantService()


@csrf_exempt
@require_http_methods(["POST"])
def voice_assistant_api(request):
    """
    API endpoint for voice assistant
    Accepts POST requests with JSON body containing:
    - message: The user's message
    - conversation_history: Optional list of previous messages
    """
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        conversation_history = data.get('conversation_history', [])
        
        if not message:
            return JsonResponse({
                'success': False,
                'error': 'No message provided'
            }, status=400)
        
        # Get user info if authenticated
        user_type = 'guest'
        user_name = 'User'
        
        if request.user.is_authenticated:
            user_type = getattr(request.user, 'user_type', 'patient')
            user_name = request.user.get_full_name() or request.user.username or 'User'
        
        # Process the message
        result = voice_assistant.process_message(
            message=message,
            user_type=user_type,
            user_name=user_name,
            conversation_history=conversation_history
        )
        
        return JsonResponse(result)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request body'
        }, status=400)
    except Exception as e:
        print(f"Voice assistant API error: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)


@require_http_methods(["GET"])
def voice_assistant_status(request):
    """
    Check if voice assistant is available
    """
    return JsonResponse({
        'available': voice_assistant.client is not None,
        'model': 'llama-3.3-70b-versatile'
    })
