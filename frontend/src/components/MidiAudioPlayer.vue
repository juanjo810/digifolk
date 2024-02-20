<template>
  <div class="midi-player hidden">
      <object id="Jazz1" classid="CLSID:1ACE1618-1C7D-4561-AEE1-34842AA85E90" class="hidden">
          <object id="Jazz2" type="audio/x-jazz" class="hidden">
              <p class="hidden;">This page requires <a href=http://jazz-soft.net>Jazz-Plugin</a>...</p> </object> </object> </div>
  </template>
  
  <script>
  //import * as MIDI from 'midicube';
  
  export default {
      name: "MidiPlayer",
      props: ["midi", "playMidi"],
      emits: ["finishedPlaying"],
      data() {
          return {
              JZZ: null,
              smf: null,
              player: null,
              out: null,
  
              saved_midi: null,
  
              playing: false,
          };
      },
      watch: {
          midi(val, oldVal) {
              if (!val || val === oldVal) return;
              this.loadMidi(val);
          },
          playMidi(val, oldVal) {
              if (val === oldVal) return;
              console.log('HERE: ');
              this.playStop();
          },
      },
      methods: {
          loadMidi(midi) {
              console.log('HERE MIDI LOAD 1')
              if (this.JZZ && midi && this.out) {
                  console.log('HERE MIDI LOAD 2')
                  if (this.playing && this.player) {
                      this.playing = false;
                      this.player.stop();
                  }
  
                  console.log('HERE MIDI LOAD 3')
                  console.log((midi))
                  this.smf = new this.JZZ.MIDI.SMF(this.JZZ.lib.fromUTF8(midi));
                  this.player = this.smf.player();
                  this.player.connect(this.out);
                  this.saved_midi = midi;
              }
          },
          playStop() {
              if (!this.playing) {
                  console.log('HERE 1')
                  console.log(this.player)
                  if (this.player) {
                      console.log('HERE 2')
                      this.playing = true;
                      this.player.onEnd = () => {
                          this.playing = false;
                          this.$emit('finishedPlaying');
                      };
                      this.player.play();
                  }
              } else {
                  console.log('HERE 3')
                  if (this.player) {
                      console.log('HERE 4')
                      this.playing = false;
                      this.player.stop();
                  }
              }
          },
      },
      mounted() {
          this.JZZ = require("jzz");
          require("jzz-midi-smf")(this.JZZ);
  
          //this.JZZMIDI(this.JZZ, MIDI);
          //this.JZZ.synth.MIDIjs({ soundfontUrl: "https://gleitz.github.io/midi-js-soundfonts/Tabla/", instrument: "synth_drum" });
          //"./soundfonts/", instrument: "acoustic_grand_piano" });
  
          require('jzz-synth-tiny')(this.JZZ);
          this.JZZ.synth.Tiny.register('Web Audio');
  
          this.JZZ.requestMIDIAccess({
              sysex: true,
          }).then(
              (access) => {
                  console.log("access", access);
                  console.log(
                      this.JZZ({
                          engine: ["webmidi"],
                          sysex: true,
                      }).info()
                  );
  
                  this.out = this.JZZ({
                          engine: ["webmidi"],
                          sysex: true,
                      })
                      .or("Cannot start MIDI engine!")
                      .openMidiOut()
                      .or("Cannot open MIDI Out!").and(function () {
                          console.log('MIDI-Out:', this.name());
                      });
              },
              (error) => console.log("error", error)
          );
          this.JZZ.close();
      },
  };
  </script>
  
  <style>
  .hidden {
      opacity: 0;
      height: 0px;
      width: 0px;
      visibility: hidden;
      display: none;
  }
  </style>