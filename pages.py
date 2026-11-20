"""Offline reference pages for Offline Crisis Kit.

Each page is a (title, markdown-ish text) pair. Supported syntax:
  # Heading, ## Subheading, "- " bullets, "1. " numbered items, **bold**.

IMPORTANT: This is a basic reference only. Content should be reviewed by
qualified people (medical, civil-protection) before real-world reliance.
Contributions and corrections are welcome.
"""

PAGES = {
    "first-aid": (
        "First Aid Basics",
        """# First Aid Basics

**This is a short reminder, not a substitute for training. If emergency services can be reached, call them first.**

## Severe bleeding
- Press firmly and directly on the wound with a clean cloth or clothing.
- Do not remove the cloth if it soaks through; add more on top and keep pressing.
- Keep pressure for at least 10 minutes without checking.
- Raise the injured limb if possible and keep the person lying down and warm.

## Person is not responsive and not breathing normally
- Call for help or send someone to get it.
- Hands-only CPR: place the heel of your hand on the center of the chest, other hand on top.
- Push hard and fast, about 5-6 cm (2 inches) deep, 100 to 120 pushes per minute.
- Do not stop until help arrives, the person starts breathing normally, or you cannot continue.

## Choking (adult, cannot speak or breathe)
- Give up to 5 firm back blows between the shoulder blades.
- Then up to 5 abdominal thrusts (stand behind, fist above the navel, pull inward and upward).
- Alternate until the object comes out or the person becomes unresponsive, then begin CPR.

## Burns
- Cool the burn under cool (not ice-cold) running water for 20 minutes.
- Remove rings and tight items near the burn before swelling starts.
- Cover loosely with a clean non-fluffy material or cling film.
- Do not apply butter, oil, toothpaste or burst blisters.
- Seek medical help for large, deep, face, hand or genital burns.

## Shock (pale, cold, clammy, fast pulse)
- Lay the person down and raise the legs slightly unless there is a leg, spine or head injury.
- Keep them warm and calm. Give nothing to eat or drink.
""",
    ),
    "water": (
        "Safe Drinking Water",
        """# Safe Drinking Water

**Always treat water of unknown quality. Clear water can still be unsafe.**

## Step 1: Clear it
- If the water is cloudy, let it settle and pour it through a clean cloth or coffee filter.

## Step 2: Disinfect (use one method)
- **Boiling (best method):** bring to a full rolling boil for 1 minute. At high altitude (above about 2000 m) boil for 3 minutes. Let it cool covered.
- **Unscented household bleach (5-9% sodium hypochlorite):** about 2 drops per liter (8 drops per gallon) of clear water. Mix, wait 30 minutes. The water should have a slight chlorine smell. If not, repeat once and wait 15 more minutes.
- **Water purification tablets:** follow the package instructions exactly.

## Storage
- Keep treated water in clean, covered containers.
- Do not use water contaminated by fuel or chemicals; boiling does not remove them.

## Quantities
- Plan at least 3 liters per person per day for drinking and basic hygiene; more in heat or for children and nursing mothers.
""",
    ),
    "comms-plan": (
        "Emergency Communication Plan",
        """# Emergency Communication Plan

## Before a crisis
- Write down key phone numbers on paper. Phones may be dead or lost.
- Agree on a meeting place near home and a second one farther away.
- Choose one out-of-area contact everyone can report to.

## During a crisis
- Send short text messages instead of calling; texts often get through when calls do not.
- Save phone battery: lower brightness, turn on battery saver, close apps.
- Use this kit's local chat to reach people on the same Wi-Fi hotspot. Use the HELP checkbox to flag urgent messages.

## Signaling for help
- Three of anything (three whistle blasts, three flashes of light, three shouts) is a widely recognized distress signal.
- Make yourself visible: bright cloth, a mirror or a phone flashlight.

## Information to give rescuers
- Your exact location or landmarks, the number of people, injuries, and what supplies you have.
""",
    ),
    "power": (
        "Power and Battery Tips",
        """# Power and Battery Tips

## Phone
- Turn on battery saver and airplane mode when you do not need the network. The local chat needs Wi-Fi hotspot, not mobile data.
- Lower screen brightness and timeout.
- Keep the phone warm; cold drains batteries quickly.

## Charging without mains power
- Power banks: keep at least one fully charged and stored with your emergency supplies.
- Solar panels (10-20 W foldable) can recharge phones slowly in daylight.
- Car chargers work while the engine runs; do not run engines in closed spaces.

## Safety
- Never charge devices on soft surfaces that trap heat.
- Do not use damaged or swollen batteries.
""",
    ),
}
