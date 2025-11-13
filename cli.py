#!/usr/bin/env python3
"""
Hue CLI - Command line interface for controlling Philips Hue lights
Designed for scripting and automation
"""
import click
import json
import sys
from typing import Optional
from hue_client import HueClient, discover_bridge
from config import (
    get_bridge_ip, set_bridge_ip,
    get_api_key, set_api_key
)


def get_client() -> Optional[HueClient]:
    """Get configured Hue client"""
    bridge_ip = get_bridge_ip()
    api_key = get_api_key()
    
    if not bridge_ip:
        click.echo("Error: Bridge IP not configured. Run 'hue-cli setup' first.", err=True)
        return None
    
    if not api_key:
        click.echo("Error: API key not configured. Run 'hue-cli setup' first.", err=True)
        return None
    
    return HueClient(bridge_ip, api_key)


@click.group()
def cli():
    """Hue CLI - Control Philips Hue lights from the command line"""
    pass


@cli.command()
def setup():
    """Initial setup: discover bridge and authenticate"""
    click.echo("Setting up Hue CLI...")
    
    # Discover bridge
    click.echo("Discovering Hue Bridge...")
    bridge_ip = discover_bridge()
    
    if not bridge_ip:
        bridge_ip = click.prompt("Bridge not found automatically. Enter bridge IP address")
    else:
        click.echo(f"Found bridge at {bridge_ip}")
        if not click.confirm("Use this bridge?", default=True):
            bridge_ip = click.prompt("Enter bridge IP address")
    
    set_bridge_ip(bridge_ip)
    
    # Create API key
    click.echo("\nPress the link button on your Hue Bridge now, then press Enter...")
    click.prompt("", default="", show_default=False)
    
    try:
        client = HueClient(bridge_ip)
        api_key = client.create_user()
        set_api_key(api_key)
        click.echo(f"\n✓ Setup complete! API key saved.")
    except ValueError as e:
        click.echo(f"\n✗ Error: {e}", err=True)
        click.echo("Make sure you pressed the link button on the bridge.", err=True)
        sys.exit(1)


@cli.command()
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def list(output_json):
    """List all lights"""
    client = get_client()
    if not client:
        sys.exit(1)
    
    try:
        lights = client.get_lights()
        
        if output_json:
            click.echo(json.dumps(lights, indent=2))
        else:
            click.echo("Lights:")
            for light_id, light_data in lights.items():
                state = light_data.get("state", {})
                on = "ON" if state.get("on") else "OFF"
                name = light_data.get("name", "Unknown")
                bri = state.get("bri", 0)
                click.echo(f"  {light_id}: {name} ({on}, brightness: {bri})")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("light_id")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def get(light_id, output_json):
    """Get state of a specific light"""
    client = get_client()
    if not client:
        sys.exit(1)
    
    try:
        light = client.get_light(light_id)
        
        if output_json:
            click.echo(json.dumps(light, indent=2))
        else:
            state = light.get("state", {})
            click.echo(f"Light {light_id}: {light.get('name', 'Unknown')}")
            click.echo(f"  On: {state.get('on', False)}")
            click.echo(f"  Brightness: {state.get('bri', 0)}")
            click.echo(f"  Hue: {state.get('hue', 'N/A')}")
            click.echo(f"  Saturation: {state.get('sat', 'N/A')}")
            click.echo(f"  Color Temperature: {state.get('ct', 'N/A')}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("light_id")
@click.option("--on/--off", default=True, help="Turn light on or off")
def on(light_id, on):
    """Turn a light on or off"""
    client = get_client()
    if not client:
        sys.exit(1)
    
    try:
        client.set_light_on(light_id, on)
        status = "on" if on else "off"
        click.echo(f"Light {light_id} turned {status}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("light_id")
@click.argument("brightness", type=click.IntRange(0, 254))
def brightness(light_id, brightness):
    """Set light brightness (0-254)"""
    client = get_client()
    if not client:
        sys.exit(1)
    
    try:
        client.set_light_brightness(light_id, brightness)
        click.echo(f"Light {light_id} brightness set to {brightness}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("light_id")
@click.option("--hue", type=int, help="Hue (0-65535)")
@click.option("--sat", type=int, help="Saturation (0-254)")
@click.option("--bri", type=int, help="Brightness (0-254)")
def color(light_id, hue, sat, bri):
    """Set light color (HSB)"""
    client = get_client()
    if not client:
        sys.exit(1)
    
    if not any([hue is not None, sat is not None, bri is not None]):
        click.echo("Error: At least one of --hue, --sat, or --bri must be specified", err=True)
        sys.exit(1)
    
    try:
        client.set_light_color(light_id, hue, sat, bri)
        click.echo(f"Light {light_id} color updated")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("light_id")
@click.argument("ct", type=click.IntRange(153, 500))
def colortemp(light_id, ct):
    """Set light color temperature in mireds (153-500, lower is cooler)"""
    client = get_client()
    if not client:
        sys.exit(1)
    
    try:
        client.set_light_color_temp(light_id, ct)
        click.echo(f"Light {light_id} color temperature set to {ct} mireds")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("light_id")
@click.argument("state_json", type=click.File('r'))
def set(light_id, state_json):
    """Set light state from JSON file"""
    client = get_client()
    if not client:
        sys.exit(1)
    
    try:
        state = json.load(state_json)
        client.set_light_state(light_id, state)
        click.echo(f"Light {light_id} state updated")
    except json.JSONDecodeError as e:
        click.echo(f"Error: Invalid JSON: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
def config():
    """Show current configuration"""
    bridge_ip = get_bridge_ip()
    api_key = get_api_key()
    
    click.echo(f"Bridge IP: {bridge_ip or 'Not configured'}")
    click.echo(f"API Key: {'Configured' if api_key else 'Not configured'}")


if __name__ == "__main__":
    cli()
