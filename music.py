import pygame
import os
import random
import numpy as np #ignore this for now 

class Music:
    def __init__(self):
        """Initialize the music system"""
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        # Audio settings
        self.music_volume = 0.3  # 30% volume for background music
        self.sfx_volume = 0.5    # 50% volume for sound effects
        self.music_enabled = True
        self.sfx_enabled = True
        
        # Background music
        self.current_music = None
        self.music_list = []
        self.music_index = 0
        
        # Sound effects
        self.sounds = {}
        
        # Initialize audio files
        self.default_beep = self.create_beep_sound(440, 300)  # 440Hz, 0.3s
        self.load_audio_files()
        
    def load_audio_files(self):
        """Load all audio files from the assets folder"""
        assets_dir = "assets"
        print(f"[DEBUG] Looking for assets directory at: {os.path.abspath(assets_dir)}")
        
        # Check if assets directory exists
        if not os.path.exists(assets_dir):
            print("Assets directory not found. Creating simple audio...")
            self.create_simple_audio()
            return
            
        # Load background music
        music_dir = os.path.join(assets_dir, "music")
        print(f"[DEBUG] Looking for music directory at: {os.path.abspath(music_dir)}")
        if os.path.exists(music_dir):
            music_files = []
            print(f"[DEBUG] Files in music directory: {os.listdir(music_dir)}")
            for file in os.listdir(music_dir):
                if file.lower().endswith(('.mp3', '.wav', '.ogg')):
                    music_path = os.path.join(music_dir, file)
                    music_files.append(music_path)
                    print(f"[DEBUG] Found music file: {music_path}")
            
            if music_files:
                self.music_list = music_files
                print(f"Loaded {len(music_files)} music files")
            else:
                print("No music files found in music directory")
        else:
            print("Music directory not found")
        
        # Load sound effects
        sfx_dir = os.path.join(assets_dir, "sounds")
        if os.path.exists(sfx_dir):
            for file in os.listdir(sfx_dir):
                if file.lower().endswith(('.mp3', '.wav', '.ogg')):
                    sfx_path = os.path.join(sfx_dir, file)
                    sound_name = os.path.splitext(file)[0]  # Remove extension
                    try:
                        self.sounds[sound_name] = pygame.mixer.Sound(sfx_path)
                        self.sounds[sound_name].set_volume(self.sfx_volume)
                        print(f"Loaded sound: {file}")
                    except Exception as e:
                        print(f"Failed to load sound {file}: {e}")
        else:
            print("Sounds directory not found")
        
        # If no audio files found, create simple ones
        if not self.music_list and not self.sounds:
            print("No audio files found, creating simple audio...")
            self.create_simple_audio()
        
        # Fallback: if no music, set music_list to [None] to trigger beep fallback
        if not self.music_list:
            print("No music files available, will use fallback beep")
            self.music_list = [None]
        
        # Fallback: if no sfx, set all keys to default beep
        for key in ['win', 'lose', 'powerup', 'item', 'level_complete']:
            if key not in self.sounds:
                self.sounds[key] = self.default_beep
    
    def create_simple_audio(self):
        """Create simple audio if no files are available"""
        print("Creating simple audio system...")
        
        # Create simple background music (beep pattern)
        self.create_simple_music()
        
        # Create simple sound effects
        self.create_simple_sounds()
    
    def create_simple_music(self):
        """Create a simple background music pattern"""
        try:
            # Create a simple melody using pygame's built-in functions
            # This is a fallback when no music files are available
            sample_rate = 44100
            duration = 2000  # 2 seconds per pattern
            
            # Create a simple repeating pattern
            self.simple_music_pattern = {
                'frequencies': [440, 494, 523, 587, 659, 587, 523, 494],  # A major scale
                'duration': duration,
                'sample_rate': sample_rate
            }
            
        except Exception as e:
            print(f"Failed to create simple music: {e}")
    
    def create_simple_sounds(self):
        """Create simple sound effects"""
        try:
            # Win sound (high pitch)
            self.sounds['win'] = self.create_beep_sound(440, 1000)  # A note for 1 second
            
            # Lose sound (low pitch)
            self.sounds['lose'] = self.create_beep_sound(220, 1000)  # Lower A note for 1 second
            
            # Power-up sound (high pitch, short)
            self.sounds['powerup'] = self.create_beep_sound(880, 200)  # High A note for 0.2 seconds
            
            # Item collection sound (medium pitch)
            self.sounds['item'] = self.create_beep_sound(660, 150)  # E note for 0.15 seconds
            
            # Level complete sound (ascending notes)
            self.sounds['level_complete'] = self.create_beep_sound(523, 500)  # C note for 0.5 seconds
            
            print("Created simple sound effects")
            
        except Exception as e:
            print(f"Failed to create simple sounds: {e}")
    
    def create_beep_sound(self, frequency, duration):
        """Create a simple beep sound"""
        try:
            sample_rate = 44100
            samples = int(sample_rate * duration / 1000)
            
            # Create a simple sine wave
            t = np.linspace(0, duration/1000, samples)
            wave = np.sin(2 * np.pi * frequency * t) * 0.3
            
            # Convert to 16-bit integer
            stereo_wave = np.column_stack((wave, wave))
            wave_int16 = (stereo_wave * 32767).astype(np.int16)
            
            # Create pygame sound
            sound = pygame.sndarray.make_sound(wave_int16)
            sound.set_volume(self.sfx_volume)
            return sound
            
        except ImportError:
            # Fallback if numpy is not available
            print("Numpy not available, using simple fallback sound")
            try:
                # Create a simple surface-based sound
                surface = pygame.Surface((100, 1))
                surface.fill((128, 128, 128))  # Gray color
                sound = pygame.sndarray.make_sound(surface)
                sound.set_volume(self.sfx_volume)
                return sound
            except Exception as e:
                print(f"Failed to create surface-based sound: {e}")
                return None
        except Exception as e:
            print(f"Failed to create beep sound: {e}")
            return None
    
    def play_background_music(self, music_file=None):
        """Play background music"""
        if not self.music_enabled:
            return
            
        try:
            # Stop any currently playing music
            pygame.mixer.music.stop()
            
            if music_file:
                # Play specific music file
                if os.path.exists(music_file):
                    pygame.mixer.music.load(music_file)
                    pygame.mixer.music.play(-1)  # Loop indefinitely
                    pygame.mixer.music.set_volume(self.music_volume)
                    self.current_music = music_file
                    print(f"Playing music: {music_file}")
                    return
                else:
                    print(f"Music file not found: {music_file}")
            elif self.music_list and self.music_list[0] is not None:
                # Play from music list
                music_file = self.music_list[self.music_index]
                if music_file and os.path.exists(music_file):
                    pygame.mixer.music.load(music_file)
                    pygame.mixer.music.play(-1)  # Loop indefinitely
                    pygame.mixer.music.set_volume(self.music_volume)
                    self.current_music = music_file
                    print(f"Playing music: {music_file}")
                    return
                else:
                    print(f"Music file not found in list: {music_file}")
            else:
                # No music files available
                print("No music files available")
                
            # Fallback: play beep in a loop
            self.play_fallback_music_loop()
                
        except Exception as e:
            print(f"Error playing background music: {e}")
            self.play_fallback_music_loop()
    
    def play_fallback_music_loop(self):
        """Play the default beep in a loop (simulate music)"""
        try:
            # Stop any current music
            pygame.mixer.music.stop()
            
            # Play the default beep in a loop
            if self.default_beep:
                # Stop any currently playing beep
                self.default_beep.stop()
                self.default_beep.play(loops=-1)
                print("Playing fallback beep music")
            else:
                print("No fallback beep available")
        except Exception as e:
            print(f"Error playing fallback music: {e}")
    
    def next_music(self):
        """Play next music in the list"""
        if self.music_list and len(self.music_list) > 1:
            self.music_index = (self.music_index + 1) % len(self.music_list)
            self.play_background_music()
        elif self.music_list and len(self.music_list) == 1:
            # If only one music file, restart it
            self.play_background_music()
    
    def previous_music(self):
        """Play previous music in the list"""
        if self.music_list and len(self.music_list) > 1:
            self.music_index = (self.music_index - 1) % len(self.music_list)
            self.play_background_music()
        elif self.music_list and len(self.music_list) == 1:
            # If only one music file, restart it
            self.play_background_music()
    
    def stop_music(self):
        """Stop background music"""
        try:
            pygame.mixer.music.stop()
            self.current_music = None
            if self.default_beep:
                self.default_beep.stop()
        except Exception as e:
            print(f"Failed to stop music: {e}")
    
    def pause_music(self):
        """Pause background music"""
        try:
            pygame.mixer.music.pause()
        except Exception as e:
            print(f"Failed to pause music: {e}")
    
    def unpause_music(self):
        """Unpause background music"""
        try:
            pygame.mixer.music.unpause()
        except Exception as e:
            print(f"Failed to unpause music: {e}")
    
    def set_music_volume(self, volume):
        """Set background music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        try:
            pygame.mixer.music.set_volume(self.music_volume)
        except Exception as e:
            print(f"Failed to set music volume: {e}")
    
    def set_sfx_volume(self, volume):
        """Set sound effects volume (0.0 to 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            if sound:
                sound.set_volume(self.sfx_volume)
    
    def play_sound(self, sound_name):
        """Play a sound effect"""
        if not self.sfx_enabled:
            return
            
        try:
            if sound_name in self.sounds and self.sounds[sound_name]:
                self.sounds[sound_name].play()
            else:
                self.default_beep.play()
        except Exception as e:
            self.default_beep.play()
    
    def play_win_sound(self):
        """Play victory sound"""
        self.play_sound('win')
    
    def play_lose_sound(self):
        """Play defeat sound"""
        self.play_sound('lose')
    
    def play_powerup_sound(self):
        """Play power-up sound"""
        self.play_sound('powerup')
    
    def play_item_sound(self):
        """Play item collection sound"""
        self.play_sound('item')
    
    def play_level_complete_sound(self):
        """Play level completion sound"""
        self.play_sound('level_complete')
    
    def toggle_music(self):
        """Toggle background music on/off"""
        self.music_enabled = not self.music_enabled
        if not self.music_enabled:
            self.stop_music()
        else:
            self.play_background_music()
    
    def toggle_sfx(self):
        """Toggle sound effects on/off"""
        self.sfx_enabled = not self.sfx_enabled
    
    def get_music_info(self):
        """Get information about current music"""
        if self.current_music:
            return {
                'current': os.path.basename(self.current_music),
                'index': self.music_index,
                'total': len(self.music_list),
                'volume': self.music_volume,
                'enabled': self.music_enabled
            }
        return None
    
    def cleanup(self):
        """Clean up audio resources"""
        try:
            self.stop_music()
            pygame.mixer.quit()
        except Exception as e:
            print(f"Failed to cleanup audio: {e}") 