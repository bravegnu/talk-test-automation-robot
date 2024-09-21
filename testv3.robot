*** Settings ***

Library  VehicleSim
Library  Display
Library  Button
Variables  setup-config.yml
Test Teardown  Reset to Default

*** Keywords ***

Reset to Default
    Sleep  5
    Stop Vehicle Simulation
    Turn OFF DUT

DUT is ON and Engaged
    Connect to Relay  ${button_serialdev}
    Set Channel  ${can_channel}
    Start Vehicle Simulation
    Turn ON DUT
    Configure RPI  ${hostname}  ${username}  ${password}

Vehicle is Moving at ${speed}kmph
    Set Vehicle Param  speed  ${speed}
    Sleep  10sec

Get Displayed Speed
    Take Screenshot
    Crop  ${img}  ${speedgauge_region}
    ${text}=  OCR  ${image}
    ${speed}=  Convert to Integer  ${text}
    RETURN  ${speed}

Verify speed gauge displayed speed <= ${expected}kmph
    ${displayed}=  Get Displayed Speed
    Should be True  ${displayed} <= ${expected}

Verify speed gauge displayed speed >= ${expected}kmph
    ${displayed}=  Get Displayed Speed
    Should be True  ${displayed} >= ${expected}

*** Test Cases ***

Test to Verify Vehicle Speed Display 100
    Given DUT is ON and Engaged
    When vehicle is moving at 100kmph
    Then verify speed gauge displayed speed >= 100kmph
    And verify speed gauge displayed speed <= 105kmph

Test to Verify Vehicle Speed Display 50
    Given DUT is ON and Engaged
    When vehicle is moving at 50kmph
    Then verify speed gauge displayed speed >= 50kmph
    And verify speed gauge displayed speed <= 52kmph
