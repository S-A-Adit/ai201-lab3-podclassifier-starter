import sys
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

def month_to_number(month_name):
    if not month_name:
        return None
    months = {
        "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
        "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12
    }
    return months.get(month_name.lower())

def safe_click(page, selectors, label):
    for sel in selectors:
        try:
            loc = page.locator(sel).first
            if loc.is_visible(timeout=1000):
                loc.click()
                print(f"  [+] Clicked {label}")
                return True
        except Exception:
            pass
    return False

def safe_fill(page, selectors, value, label):
    if not value:
        return False
    for sel in selectors:
        try:
            loc = page.locator(sel).first
            if loc.is_visible(timeout=1000):
                loc.fill(value)
                print(f"  [+] Filled {label}: '{value}'")
                return True
        except Exception:
            pass
    return False

def fill_autocomplete(page, selectors, value, label):
    if not value:
        return False
    for sel in selectors:
        try:
            loc = page.locator(sel).first
            if loc.is_visible(timeout=1000):
                loc.fill(value)
                page.wait_for_timeout(1000)  # Wait for suggestions to render
                loc.press("ArrowDown")
                page.wait_for_timeout(500)
                loc.press("Enter")
                print(f"  [+] Filled autocomplete for {label}: '{value}'")
                return True
        except Exception:
            pass
    return False

def select_dropdown(page, selectors, value, label):
    if not value:
        return False
    for sel in selectors:
        try:
            loc = page.locator(sel).first
            if loc.is_visible(timeout=1000):
                # Try by label text
                try:
                    loc.select_option(label=value)
                    print(f"  [+] Selected {label} (by text): {value}")
                    return True
                except Exception:
                    pass
                
                # Try by numerical value
                m_num = month_to_number(value)
                if m_num is not None:
                    try:
                        loc.select_option(value=str(m_num))
                        print(f"  [+] Selected {label} (by numerical value): {m_num}")
                        return True
                    except Exception:
                        pass
                    try:
                        loc.select_option(value=f"{m_num:02d}")
                        print(f"  [+] Selected {label} (by padded numerical value): {m_num:02d}")
                        return True
                    except Exception:
                        pass
        except Exception:
            pass
    return False

def fill_education_section(page, education_list):
    print("\n--- Filling Education Section ---")
    if not education_list:
        print("[*] No education records found in profile.")
        return
        
    for edu in education_list:
        print(f"\nAdding Education: {edu.get('degree')} in {edu.get('major')} at {edu.get('school')}")
        print("Please verify the 'Add Education' modal is open, or click '+' in the Education section in the browser.")
        
        # Click Add Education
        safe_click(page, [
            "button:has-text('Add Education')", 
            "button:has-text('Add School')", 
            "section:has-text('Education') button",
            "a:has-text('Add Education')"
        ], "Add School button")
        
        page.wait_for_timeout(1000)
        
        # School
        fill_autocomplete(page, [
            "input[placeholder*='school']", 
            "input[id*='school']", 
            "input[name*='school']"
        ], edu.get("school"), "School")
        
        # Degree
        fill_autocomplete(page, [
            "input[placeholder*='degree']",
            "input[id*='degree']",
            "input[name*='degree']",
            "select[name*='degree']"
        ], edu.get("degree"), "Degree")
        
        # Major
        fill_autocomplete(page, [
            "input[placeholder*='major']",
            "input[id*='major']",
            "input[name*='major']"
        ], edu.get("major"), "Major")
        
        # GPA
        safe_fill(page, [
            "input[placeholder*='GPA']",
            "input[id*='gpa']",
            "input[name*='gpa']"
        ], edu.get("gpa"), "GPA")
        
        # Start Date
        select_dropdown(page, ["select[name*='start_month']", "select[id*='start_month']"], edu.get("start_month"), "Start Month")
        safe_fill(page, ["input[name*='start_year']", "select[name*='start_year']"], edu.get("start_year"), "Start Year")
        
        # End Date
        if edu.get("is_current"):
            safe_click(page, ["input[type='checkbox'][name*='current']", "label:has-text('currently')"], "Currently Attending checkbox")
        else:
            select_dropdown(page, ["select[name*='end_month']", "select[id*='end_month']"], edu.get("end_month"), "End Month")
            safe_fill(page, ["input[name*='end_year']", "select[name*='end_year']"], edu.get("end_year"), "End Year")
            
        print("\n--> ACTION REQUIRED: Verify the form fields in the browser.")
        print("    If needed, click the correct autocomplete suggestions or adjust dropdowns.")
        choice = input("    Press [Enter] when ready to save and continue, or type 's' to skip/cancel: ")
        
        if choice.lower() != 's':
            print("Saving...")
            saved = safe_click(page, [
                "button:has-text('Save')", 
                "button[type='submit']",
                "button:has-text('Add School')",
                "button:has-text('Add Education')"
            ], "Save Button")
            if not saved:
                input("    Auto-save button not found. Please click 'Save' in the browser, then press [Enter] to continue: ")
        else:
            print("Skipped.")
            safe_click(page, ["button:has-text('Cancel')", "button:has-text('Close')"], "Cancel Button")

def fill_experience_section(page, experience_list):
    print("\n--- Filling Work Experience Section ---")
    if not experience_list:
        print("[*] No experience records found in profile.")
        return
        
    for exp in experience_list:
        print(f"\nAdding Experience: {exp.get('role')} at {exp.get('employer')}")
        print("Please verify the 'Add' modal is open, or click '+' in the Work Experience section in the browser.")
        
        # Click Add Experience
        safe_click(page, [
            "button:has-text('Add Work Experience')",
            "button:has-text('Add Experience')",
            "section:has-text('Work Experience') button",
            "section:has-text('Experience') button"
        ], "Add Experience button")
        
        page.wait_for_timeout(1000)
        
        # Employer
        fill_autocomplete(page, [
            "input[placeholder*='employer']",
            "input[placeholder*='company']",
            "input[id*='employer']",
            "input[name*='employer']"
        ], exp.get("employer"), "Employer")
        
        # Role
        safe_fill(page, [
            "input[placeholder*='role']",
            "input[placeholder*='title']",
            "input[id*='title']",
            "input[name*='role']",
            "input[name*='title']"
        ], exp.get("role"), "Job Title")
        
        # Location
        safe_fill(page, [
            "input[placeholder*='location']",
            "input[id*='location']",
            "input[name*='location']"
        ], exp.get("location"), "Location")
        
        # Dates
        select_dropdown(page, ["select[name*='start_month']", "select[id*='start_month']"], exp.get("start_month"), "Start Month")
        safe_fill(page, ["input[name*='start_year']", "select[name*='start_year']"], exp.get("start_year"), "Start Year")
        
        if exp.get("is_current"):
            safe_click(page, ["input[type='checkbox'][name*='current']", "label:has-text('currently')"], "Currently Work Here checkbox")
        else:
            select_dropdown(page, ["select[name*='end_month']", "select[id*='end_month']"], exp.get("end_month"), "End Month")
            safe_fill(page, ["input[name*='end_year']", "select[name*='end_year']"], exp.get("end_year"), "End Year")
            
        # Description
        safe_fill(page, [
            "textarea[name*='description']",
            "textarea[id*='description']",
            "textarea"
        ], exp.get("description"), "Description")
        
        print("\n--> ACTION REQUIRED: Verify the form fields in the browser.")
        print("    If needed, click the correct autocomplete suggestions or adjust dropdowns.")
        choice = input("    Press [Enter] when ready to save and continue, or type 's' to skip/cancel: ")
        
        if choice.lower() != 's':
            print("Saving...")
            saved = safe_click(page, [
                "button:has-text('Save')", 
                "button[type='submit']",
                "button:has-text('Add Experience')"
            ], "Save Button")
            if not saved:
                input("    Auto-save button not found. Please click 'Save' in the browser, then press [Enter] to continue: ")
        else:
            print("Skipped.")
            safe_click(page, ["button:has-text('Cancel')", "button:has-text('Close')"], "Cancel Button")

def fill_projects_section(page, projects_list):
    print("\n--- Filling Projects Section ---")
    if not projects_list:
        print("[*] No projects found in profile.")
        return
        
    for proj in projects_list:
        print(f"\nAdding Project: {proj.get('title')}")
        print("Please verify the 'Add Project' modal is open, or click '+' in the Projects section in the browser.")
        
        # Click Add Project
        safe_click(page, [
            "button:has-text('Add Project')",
            "section:has-text('Projects') button"
        ], "Add Project button")
        
        page.wait_for_timeout(1000)
        
        # Title
        safe_fill(page, [
            "input[placeholder*='project']",
            "input[id*='title']",
            "input[name*='title']"
        ], proj.get("title"), "Project Title")
        
        # Dates
        select_dropdown(page, ["select[name*='start_month']", "select[id*='start_month']"], proj.get("start_month"), "Start Month")
        safe_fill(page, ["input[name*='start_year']", "select[name*='start_year']"], proj.get("start_year"), "Start Year")
        
        if proj.get("is_current"):
            safe_click(page, ["input[type='checkbox'][name*='current']", "label:has-text('currently')"], "Currently working on this checkbox")
        else:
            select_dropdown(page, ["select[name*='end_month']", "select[id*='end_month']"], proj.get("end_month"), "End Month")
            safe_fill(page, ["input[name*='end_year']", "select[name*='end_year']"], proj.get("end_year"), "End Year")
            
        # Description
        safe_fill(page, [
            "textarea[name*='description']",
            "textarea[id*='description']",
            "textarea"
        ], proj.get("description"), "Description")
        
        # URL
        safe_fill(page, [
            "input[name*='url']",
            "input[placeholder*='http']",
            "input[id*='link']"
        ], proj.get("url"), "Project URL")
        
        print("\n--> ACTION REQUIRED: Verify the form fields in the browser.")
        choice = input("    Press [Enter] when ready to save and continue, or type 's' to skip/cancel: ")
        
        if choice.lower() != 's':
            print("Saving...")
            saved = safe_click(page, [
                "button:has-text('Save')", 
                "button[type='submit']",
                "button:has-text('Add Project')"
            ], "Save Button")
            if not saved:
                input("    Auto-save button not found. Please click 'Save' in the browser, then press [Enter] to continue: ")
        else:
            print("Skipped.")
            safe_click(page, ["button:has-text('Cancel')", "button:has-text('Close')"], "Cancel Button")

def fill_organizations_section(page, org_list):
    print("\n--- Filling Organizations Section ---")
    if not org_list:
        print("[*] No organizations found in profile.")
        return
        
    for org in org_list:
        print(f"\nAdding Organization: {org.get('role')} at {org.get('organization')}")
        print("Please verify the 'Add Organization' modal is open, or click '+' in the Organizations section in the browser.")
        
        # Click Add Organization
        safe_click(page, [
            "button:has-text('Add Organization')",
            "button:has-text('Add Activity')",
            "section:has-text('Organizations') button"
        ], "Add Organization button")
        
        page.wait_for_timeout(1000)
        
        # Organization Name
        safe_fill(page, [
            "input[placeholder*='organization']",
            "input[placeholder*='activity']",
            "input[id*='organization']",
            "input[name*='organization']"
        ], org.get("organization"), "Organization Name")
        
        # Role
        safe_fill(page, [
            "input[placeholder*='role']",
            "input[placeholder*='position']",
            "input[id*='role']",
            "input[name*='role']"
        ], org.get("role"), "Role")
        
        # Dates
        select_dropdown(page, ["select[name*='start_month']", "select[id*='start_month']"], org.get("start_month"), "Start Month")
        safe_fill(page, ["input[name*='start_year']", "select[name*='start_year']"], org.get("start_year"), "Start Year")
        
        if org.get("is_current"):
            safe_click(page, ["input[type='checkbox'][name*='current']", "label:has-text('currently')"], "Currently involved checkbox")
        else:
            select_dropdown(page, ["select[name*='end_month']", "select[id*='end_month']"], org.get("end_month"), "End Month")
            safe_fill(page, ["input[name*='end_year']", "select[name*='end_year']"], org.get("end_year"), "End Year")
            
        # Description
        safe_fill(page, [
            "textarea[name*='description']",
            "textarea[id*='description']",
            "textarea"
        ], org.get("description"), "Description")
        
        print("\n--> ACTION REQUIRED: Verify the form fields in the browser.")
        choice = input("    Press [Enter] when ready to save and continue, or type 's' to skip/cancel: ")
        
        if choice.lower() != 's':
            print("Saving...")
            saved = safe_click(page, [
                "button:has-text('Save')", 
                "button[type='submit']",
                "button:has-text('Add Organization')"
            ], "Save Button")
            if not saved:
                input("    Auto-save button not found. Please click 'Save' in the browser, then press [Enter] to continue: ")
        else:
            print("Skipped.")
            safe_click(page, ["button:has-text('Cancel')", "button:has-text('Close')"], "Cancel Button")

def fill_skills_section(page, skills_list):
    print("\n--- Filling Skills Section ---")
    if not skills_list:
        print("[*] No skills found in profile.")
        return
        
    print(f"Skills to add: {', '.join(skills_list)}")
    print("Please verify the 'Add Skills' input is visible, or click '+' in the Skills section in the browser.")
    
    # Try to click Add Skills button
    safe_click(page, [
        "button:has-text('Add Skills')",
        "button:has-text('Add Skill')",
        "section:has-text('Skills') button"
    ], "Add Skills button")
    
    page.wait_for_timeout(1000)
    
    input_selectors = [
        "input[placeholder*='skill']",
        "input[id*='skill']",
        "section:has-text('Skills') input"
    ]
    
    # Locate the input field
    skill_input = None
    for selector in input_selectors:
        try:
            el = page.locator(selector).first
            if el.is_visible(timeout=1000):
                skill_input = el
                break
        except Exception:
            pass
            
    if not skill_input:
        print("[!] Could not locate Skills input field automatically.")
        input("Please open the Skills modal/input field in the browser, then press [Enter] here...")
        # Try finding it again
        for selector in input_selectors:
            try:
                el = page.locator(selector).first
                if el.is_visible(timeout=1000):
                    skill_input = el
                    break
            except Exception:
                pass
                
    if skill_input:
        for skill in skills_list:
            print(f"Typing skill: {skill}")
            try:
                skill_input.fill(skill)
                page.wait_for_timeout(800)  # Wait for dropdown autocomplete options
                skill_input.press("Enter")
                page.wait_for_timeout(600)  # Wait for it to register in UI list
            except Exception as e:
                print(f"  [!] Failed to enter skill '{skill}': {e}")
                
        print("\n--> ACTION REQUIRED: Verify the added skills in the browser.")
        choice = input("    Press [Enter] when ready to save and continue, or type 's' to skip/cancel: ")
        
        if choice.lower() != 's':
            print("Saving...")
            saved = safe_click(page, [
                "button:has-text('Save')", 
                "button[type='submit']",
                "button:has-text('Add')"
            ], "Save Button")
            if not saved:
                input("    Auto-save button not found. Please click 'Save' in the browser, then press [Enter] to continue: ")
        else:
            print("Skipped.")
            safe_click(page, ["button:has-text('Cancel')", "button:has-text('Close')"], "Cancel Button")

def run_filler():
    profile_json_path = Path(__file__).parent / "profile.json"
    if not profile_json_path.exists():
        print(f"[!] profile.json not found at {profile_json_path}. Please run parser.py first.")
        sys.exit(1)
        
    with open(profile_json_path, "r", encoding="utf-8") as f:
        profile_data = json.load(f)
        
    print("[*] Launching Playwright browser...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # Navigate to Handshake login
        print("[*] Opening Handshake login page...")
        page.goto("https://app.joinhandshake.com/login")
        
        print("\n=======================================================")
        print("ACTION REQUIRED:")
        print("1. Log in to your Handshake account in the browser window.")
        print("2. Navigate to your Profile page.")
        print("   (Usually by clicking your name/photo top-right -> 'My Profile')")
        print("=======================================================")
        
        input("\n--> Press [Enter] here once you are on your Handshake profile page...")
        
        current_url = page.url
        print(f"[*] Connected and ready. Current URL: {current_url}")
        
        while True:
            print("\n=================================")
            print("=== Handshake Autofill Menu ===")
            print("1. Fill Education")
            print("2. Fill Work Experience")
            print("3. Fill Projects")
            print("4. Fill Organizations")
            print("5. Fill Skills")
            print("6. Run All Sections (Step-by-step)")
            print("Q. Quit")
            print("=================================")
            
            choice = input("\nChoose an option (1-6, Q): ").strip().upper()
            
            if choice == "1":
                fill_education_section(page, profile_data.get("education", []))
            elif choice == "2":
                fill_experience_section(page, profile_data.get("experience", []))
            elif choice == "3":
                fill_projects_section(page, profile_data.get("projects", []))
            elif choice == "4":
                fill_organizations_section(page, profile_data.get("organizations", []))
            elif choice == "5":
                fill_skills_section(page, profile_data.get("skills", []))
            elif choice == "6":
                fill_education_section(page, profile_data.get("education", []))
                fill_experience_section(page, profile_data.get("experience", []))
                fill_projects_section(page, profile_data.get("projects", []))
                fill_organizations_section(page, profile_data.get("organizations", []))
                fill_skills_section(page, profile_data.get("skills", []))
                print("\n[+] Finished running all sections!")
            elif choice == "Q":
                print("[*] Closing browser and exiting. Good luck with your Handshake profile!")
                break
            else:
                print("[!] Invalid option. Please choose 1-6 or Q.")
                
        browser.close()

if __name__ == "__main__":
    run_filler()
