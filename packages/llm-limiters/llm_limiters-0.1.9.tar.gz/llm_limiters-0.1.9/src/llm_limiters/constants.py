GEMINI_LIVE_LIMITS = {
    "free": {
        "gemini-2.0-flash-live-001": {"rpm": 10, "tpm": 1_000_000, "rpd": 200}, 
    },
    "tier1": {
        "gemini-2.0-flash-live-001": {"rpm": 50, "tpm": 4_000_000, "rpd": 10_000},
    },
    "tier2": {
        "gemini-2.0-flash-live-001": {"rpm": 1_000, "tpm": 10_000_000, "rpd": 50_000},
    },
    "tier3": {
        "gemini-2.0-flash-live-001": {"rpm": 5_000, "tpm": 100_000_000, "rpd": float('inf')},
    }
}

GEMINI_API_LIMITS = {
    "free": {
        "gemini-2.5-pro": {"rpm": 5, "tpm": 250_000, "rpd": 100},
        "gemini-2.5-flash": {"rpm": 10, "tpm": 250_000, "rpd": 250},
        "gemini-2.5-flash-lite": {"rpm": 15, "tpm": 250_000, "rpd": 1_000},
        "gemini-2.0-flash": {"rpm": 15, "tpm": 1_000_000, "rpd": 200},
        "gemini-2.0-flash-lite": {"rpm": 30, "tpm": 1_000_000, "rpd": 200},
    },
    "tier1": {
        "gemini-2.5-pro": {"rpm": 150, "tpm": 2_000_000, "rpd": 10_000},
        "gemini-2.5-flash": {"rpm": 1_000, "tpm": 1_000_000, "rpd": 10_000},
        "gemini-2.5-flash-lite": {"rpm": 4_000, "tpm": 4_000_000, "rpd": float('inf')},
        "gemini-2.0-flash": {"rpm": 2_000, "tpm": 4_000_000, "rpd": float('inf')},
        "gemini-2.0-flash-lite": {"rpm": 4_000, "tpm": 4_000_000, "rpd": float('inf')},
    },
    "tier2": {
        "gemini-2.5-pro": {"rpm": 1_000, "tpm": 5_000_000, "rpd": 50_000},
        "gemini-2.5-flash": {"rpm": 2_000, "tpm": 3_000_000, "rpd": 100_000},
        "gemini-2.5-flash-lite": {"rpm": 10_000, "tpm": 10_000_000, "rpd": float('inf')},
        "gemini-2.0-flash": {"rpm": 10_000, "tpm": 10_000_000, "rpd": float('inf')},
        "gemini-2.0-flash-lite": {"rpm": 20_000, "tpm": 10_000_000, "rpd": float('inf')},
    },
    "tier3": {
        "gemini-2.5-pro": {"rpm": 2_000, "tpm": 8_000_000, "rpd": float('inf')},
        "gemini-2.5-flash": {"rpm": 10_000, "tpm": 8_000_000, "rpd": float('inf')},
        "gemini-2.5-flash-lite": {"rpm": 30_000, "tpm": 30_000_000, "rpd": float('inf')},
        "gemini-2.0-flash": {"rpm": 30_000, "tpm": 30_000_000, "rpd": float('inf')},
        "gemini-2.0-flash-lite": {"rpm": 30_000, "tpm": 30_000_000, "rpd": float('inf')},
    }
}

OPENAI_API_LIMITS = {
    "free": {
        "gpt-4o-mini": {"rpm": 50, "tpm": 200000, "rpd": float("inf")},
        "gpt-4.1": {"rpm": 30, "tpm": 300000, "rpd": float("inf")},
        "gpt-4o": {"rpm": 15, "tpm": 300000, "rpd": float("inf")},
    },
    "tier1": {
        "gpt-4o-mini": {"rpm": 200, "tpm": 2000000, "rpd": float("inf")},
        "gpt-4.1": {"rpm": 150, "tpm": 2000000, "rpd": float("inf")},
        "gpt-4o": {"rpm": 80, "tpm": 2000000, "rpd": float("inf")},
    },
}

# constants_image.py

GEMINI_IMAGE_LIMITS = {
    "free": {},
    "tier1": {
        "gemini-2.5-flash-image": {
            "rpm": 500,
            "tpm": 500_000,
            "rpd": 2_000
        },
        "gemini-3-pro-image": {
            "rpm": 20,
            "tpm": 100_000,
            "rpd": 250
        },
        "imagen-4.0-fast-generate-001": {
            "rpm": 10,
            "tpm": 0,   
            "rpd": 70
        },
        "imagen-4.0-generate-001": {
            "rpm": 10,
            "tpm": 0,
            "rpd": 70
        },
        "imagen-4.0-ultra-generate-001": {
            "rpm": 5,
            "tpm": 0,
            "rpd": 30
        }
    },

    "tier2": {},
    "tier3": {}
}


OPENAI_IMAGE_LIMITS = {
    "free": {
        # OpenAI image models are NOT available on free tier
    },

    "tier1": {
        "gpt-image-1": {
            "rpm": 5,
            "tpm": 100_000,
            "rpd": 0  # OpenAI does not enforce RPD
        },
        "gpt-image-1-mini": {
            "rpm": 5,
            "tpm": 100_000,
            "rpd": 0
        }
    },

    "tier2": {
        "gpt-image-1": {
            "rpm": 20,
            "tpm": 250_000,
            "rpd": 0
        },
        "gpt-image-1-mini": {
            "rpm": 20,
            "tpm": 250_000,
            "rpd": 0
        }
    },

    "tier3": {
        "gpt-image-1": {
            "rpm": 50,
            "tpm": 800_000,
            "rpd": 0
        },
        "gpt-image-1-mini": {
            "rpm": 50,
            "tpm": 800_000,
            "rpd": 0
        }
    },

    "tier4": {
        "gpt-image-1": {
            "rpm": 150,
            "tpm": 3_000_000,
            "rpd": 0
        },
        "gpt-image-1-mini": {
            "rpm": 150,
            "tpm": 3_000_000,
            "rpd": 0
        }
    },

    "tier5": {
        "gpt-image-1": {
            "rpm": 250,
            "tpm": 8_000_000,
            "rpd": 0
        },
        "gpt-image-1-mini": {
            "rpm": 250,
            "tpm": 8_000_000,
            "rpd": 0
        }
    }
}

# OpenAI Audio / TTS limits
OPENAI_AUDIO_LIMITS = {
    "free": {
        "tts-1": {
            "rpm": 3,
            "tpm": 0,
            "rpd": 200
        }
    },

    "tier1": {
        "tts-1": {
            "rpm": 500,
            "tpm": 0,
            "rpd": 0
        },
        "tts-1-hd": {
            "rpm": 500,
            "tpm": 0,
            "rpd": 0
        },
        "gpt-4o-mini-tts": {
            "rpm": 500,
            "tpm": 50_000,
            "rpd": 0
        }
    },

    "tier2": {
        "tts-1": {
            "rpm": 2_500,
            "tpm": 0,
            "rpd": 0
        },
        "tts-1-hd": {
            "rpm": 2_500,
            "tpm": 0,
            "rpd": 0
        },
        "gpt-4o-mini-tts": {
            "rpm": 2_000,
            "tpm": 150_000,
            "rpd": 0
        }
    },

    "tier3": {
        "tts-1": {
            "rpm": 5_000,
            "tpm": 0,
            "rpd": 0
        },
        "tts-1-hd": {
            "rpm": 5_000,
            "tpm": 0,
            "rpd": 0
        },
        "gpt-4o-mini-tts": {
            "rpm": 5_000,
            "tpm": 500_000,
            "rpd": 0
        }
    },

    "tier4": {
        "tts-1": {
            "rpm": 7_500,
            "tpm": 0,
            "rpd": 0
        },
        "tts-1-hd": {
            "rpm": 7_500,
            "tpm": 0,
            "rpd": 0
        },
        "gpt-4o-mini-tts": {
            "rpm": 10_000,
            "tpm": 2_000_000,
            "rpd": 0
        }
    },

    "tier5": {
        "tts-1": {
            "rpm": 10_000,
            "tpm": 0,
            "rpd": 0
        },
        "tts-1-hd": {
            "rpm": 10_000,
            "tpm": 0,
            "rpd": 0
        },
        "gpt-4o-mini-tts": {
            "rpm": 10_000,
            "tpm": 8_000_000,
            "rpd": 0
        }
    }
}

# Gemini audio / TTS / native-audio models

GEMINI_AUDIO_LIMITS = {
    "free": {
        "gemini-2.5-flash-native-audio-dialog": {
            "rpm": float("inf"), 
            "tpm": 1_000_000,  
            "rpd": float("inf") 
        },
        "gemini-2.5-flash-tts": {
            "rpm": 3,
            "tpm": 10_000,
            "rpd": 10
        }
    },

    "tier1": {
        "gemini-2.5-flash-native-audio-dialog": {
            "rpm": float("inf"),
            "tpm": 1_000_000,
            "rpd": float("inf")
        },
        "gemini-2.5-flash-tts": {
            "rpm": 10,
            "tpm": 10_000,
            "rpd": 100
        },
        "gemini-2.5-pro-tts": {
            "rpm": 10,
            "tpm": 10_000,
            "rpd": 50
        }
    },

    "tier2": {
        "gemini-2.5-flash-native-audio-dialog": {
            "rpm": float("inf"),
            "tpm": 4_000_000,
            "rpd": float("inf")
        },
        "gemini-2.5-flash-tts": {
            "rpm": 50,
            "tpm": 10_000,
            "rpd": 500
        },
        "gemini-2.5-pro-tts": {
            "rpm": 50,
            "tpm": 10_000,
            "rpd": 250
        }
    },

    "tier3": {
        "gemini-2.5-flash-native-audio-dialog": {
            "rpm": float("inf"),
            "tpm": 10_000_000,
            "rpd": float("inf")
        },
        "gemini-2.5-flash-tts": {
            "rpm": 100,
            "tpm": 10_000,
            "rpd": float("inf")
        },
        "gemini-2.5-pro-preview-tts": {
            "rpm": 100,
            "tpm": 10_000,
            "rpd": float("inf")
        }
    }
}
