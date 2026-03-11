
def get_nvidia_client() -> Optional[NVIDIAClient]:
    """Get singleton instance of NVIDIAClient."""
    try:
        if not hasattr(get_nvidia_client, '_instance'):
            get_nvidia_client._instance = NVIDIAClient()
        return get_nvidia_client._instance
    except Exception as e:
        print(f"Failed to initialize NVIDIA client: {e}")
        return None
