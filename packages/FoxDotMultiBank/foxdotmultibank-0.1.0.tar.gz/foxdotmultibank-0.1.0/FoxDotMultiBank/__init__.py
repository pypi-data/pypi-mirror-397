import os
from os.path import join
from pathlib import Path

from FoxDot.lib.Buffers import (
    BufferManager,
    GranularSynthDef,
    LoopSynthDef,
    SampleSynthDef,
    StretchSynthDef,
    nil,
    nonalpha,
    _symbolToDir,
)
from FoxDot.lib.Players import Player
from FoxDot.lib.Scale import get_freq_and_midi
from FoxDot.lib.Settings import FOXDOT_SND, LoopPlayer, SamplePlayer

__all__ = ['Samples', 'Player', 'symbolToDir', 'loop', 'stretch', 'gsynth']

DEFAULT_SAMPLES_BANK = Path(FOXDOT_SND)


def new_message_header(self, event, **kwargs):
    """Returns the header of an osc message to be added to by osc_message()"""
    # Let SC know the duration of 1 beat so effects can use it and adjust sustain too
    beat_dur = self.metro.beat_dur()
    # print(event)
    message = {
        'beat_dur': beat_dur,
        'sus': kwargs.get('sus', event['sus']) * beat_dur,
    }
    if self.synthdef == SamplePlayer:
        degree = kwargs.get('degree', event['degree'])
        sample = kwargs.get('sample', event['sample'])
        rate = kwargs.get('rate', event['rate'])
        if rate < 0:
            sus = kwargs.get('sus', event['sus'])
            pos = self.metro.beat_dur(sus)
        else:
            pos = 0
        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        if (bank := kwargs.get('bank', event.get('bank'))) is None:
            if (bank := kwargs.get('spack', event.get('spack'))) is None:
                if (bank := kwargs.get('sdb', event.get('sdb'))) is None:
                    bank = 0
        buf = self.samples.getBufferFromSymbol(
            str(degree), bank, sample
        ).bufnum
        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        message.update({'buf': buf, 'pos': pos})
        # Update player key
        if 'buf' in self.accessed_keys:
            self.buf = buf
    elif self.synthdef == LoopPlayer:
        # print(event)
        pos = kwargs.get('degree', event['degree'])
        buf = kwargs.get('buf', event['buf'])
        # Get a user-specified tempo
        given_tempo = kwargs.get(
            'tempo', self.event.get('tempo', self.metro.bpm)
        )
        if given_tempo in (None, 0):
            tempo = 1
        else:
            tempo = self.metro.bpm / given_tempo
        # Set the position in "beats"
        pos = pos * tempo * self.metro.beat_dur(1)
        # If there is a negative rate, move the pos forward
        rate = kwargs.get('rate', event['rate'])
        if rate == 0:
            rate = 1
        # Adjust the rate to a given tempo
        rate = float(tempo * rate)
        if rate < 0:
            sus = kwargs.get('sus', event['sus'])
            pos += self.metro.beat_dur(sus)
        message.update({'pos': pos, 'buf': buf, 'rate': rate})
    else:
        degree = kwargs.get('degree', event['degree'])
        octave = kwargs.get('oct', event['oct'])
        root = kwargs.get('root', event['root'])
        scale = kwargs.get('scale', self.scale)
        if degree is None:
            freq, midinote = None, None
        else:
            freq, midinote = get_freq_and_midi(degree, octave, root, scale)
        message.update({'freq': freq, 'midinote': midinote})
        # Updater player key
        if 'freq' in self.accessed_keys:
            self.freq = freq
        if 'midinote' in self.accessed_keys:
            self.midinote = midinote
    # Update the dict with other values from the event
    event.update(message)
    # Remove keys we dont need
    del event['bpm']
    return event


setattr(Player, 'new_message_header', new_message_header)


class SymbolToDir(_symbolToDir):
    def __call__(self, symbol, bank_path):
        """Return the sample search directory for a symbol"""
        if symbol.isalpha():
            return join(
                bank_path,
                symbol.lower(),
                'upper' if symbol.isupper() else 'lower',
            )
        if symbol in nonalpha:
            longname = nonalpha[symbol]
            return join(bank_path, '_', longname)


symbolToDir = SymbolToDir(FOXDOT_SND)  # singleton


class SampleManager(BufferManager):
    banks = {0: DEFAULT_SAMPLES_BANK}

    def getBufferFromSymbol(
        self, symbol, bank=0, index=0
    ):  # pylint: disable=invalid-name
        """
        Get buffer information from a symbol.
        ---
        d1 >> play('x-', bank=1)
        """
        if symbol.isspace():
            return nil

        bank_path = self.banks.get(bank, self.banks[0])
        sample_path = symbolToDir(symbol, bank_path)
        if sample_path is None:
            return nil

        # sample_path = self._findSample(sample_path, index, bank)
        sample_path = self._findSample(sample_path, index)
        if sample_path is None:
            return nil

        return self._allocateAndLoad(sample_path)

    def addBank(self, bank_path):
        bank = Path(bank_path)
        self.banks[len(self.banks)] = bank

        loops = bank / '_loop_'
        if loops.exists():
            # compartilhar o todos os loops sem precisar trocar de banco
            self.addPath(loops)

    @property
    def loops(self):
        """Sorted list of available loops."""
        return sorted(
            {
                loop
                for path in self._paths
                for filename in os.listdir(path)
                if (loop := filename.rsplit('.', 1)[0])
            },
        )

    @loops.setter
    def loops(self, _):
        ...


Samples = SampleManager()
Player.set_sample_bank(Samples)


class LSD(LoopSynthDef):
    def __call__(self, filename, pos=0, sample=0, **kwargs):
        # << reflecting Player.set_sample_bank
        kwargs['buf'] = Player.samples.loadBuffer(filename, sample)
        # TODO: usar o arg `bank=1` pra mudar o banco de samples/loops
        proxy = SampleSynthDef.__call__(self, pos, **kwargs)
        proxy.kwargs['filename'] = filename
        return proxy


class SSD(StretchSynthDef):
    def __call__(self, filename, pos=0, sample=0, **kwargs):
        # << reflecting Player.set_sample_bank
        kwargs['buf'] = Player.samples.loadBuffer(filename, sample)
        proxy = SampleSynthDef.__call__(self, pos, **kwargs)
        proxy.kwargs['filename'] = filename
        return proxy


class GSD(GranularSynthDef):
    def __call__(self, filename, pos=0, sample=0, **kwargs):
        # << reflecting Player.set_sample_bank
        kwargs['buf'] = Player.samples.loadBuffer(filename, sample)
        return SampleSynthDef.__call__(self, pos, **kwargs)


loop = LSD()
stretch = SSD()
gsynth = GSD()
