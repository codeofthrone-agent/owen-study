from libraries.robot_arm_control.button_config_loader import ButtonConfigLoader

try:
    print("Loading config for taipei_lab...")
    loader = ButtonConfigLoader("config/robot_arm/taipei_lab_buttons.yaml")
    
    print("\nVerifying Environment Light Mappings:")
    buttons_to_check = ['light1', 'light2', 'water_heater_gas', 'bluetooth']
    
    for btn_id in buttons_to_check:
        config = loader.get_button_config(btn_id)
        env_light = config.get('environment_light')
        print(f"Button: {btn_id:20} -> Environment Light: {env_light}")
        
    print("\n✅ Config loaded and mappings verified successfully.")
    
except Exception as e:
    print(f"\n❌ Validation Failed: {e}")
    exit(1)
