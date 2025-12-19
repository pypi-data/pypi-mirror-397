from __future__ import annotations
import ostk.core.type
import ostk.physics.coordinate
import ostk.physics.environment
import typing
from . import spice
__all__ = ['Analytical', 'SPICE', 'spice']
class Analytical(ostk.physics.environment.Ephemeris):
    """
    
                Analytical ephemeris.
    
                An analytical ephemeris that uses a reference frame to provide
                position and orientation information. This is typically used
                for celestial objects whose positions can be computed analytically
                from the reference frame transformations.
    
                Args:
                    frame (Frame): The reference frame for this ephemeris.
    
                Example:
                    >>> from ostk.physics.environment.ephemeris import Analytical
                    >>> from ostk.physics.coordinate import Frame
                    >>> analytical = Analytical(Frame.GCRF())
            
    """
    def __init__(self, frame: ostk.physics.coordinate.Frame) -> None:
        """
                        Constructor.
        
                        Args:
                            frame (Frame): The reference frame for this ephemeris.
        """
class SPICE(ostk.physics.environment.Ephemeris):
    """
    
                SPICE Toolkit ephemeris.
    
                Provides ephemeris data using NASA's SPICE Toolkit. SPICE (Spacecraft Planet
                Instrument C-matrix Events) is an observation geometry information system
                used by NASA's planetary science missions.
    
                The SPICE ephemeris supports various celestial objects including the Sun,
                planets, and the Moon.
    
                Args:
                    object (SPICE.Object): The SPICE object for this ephemeris.
    
                Example:
                    >>> from ostk.physics.environment.ephemeris import SPICE
                    >>> spice_ephemeris = SPICE(SPICE.Object.Earth)
    
                See Also:
                    https://naif.jpl.nasa.gov/naif/
            
    """
    class Object:
        """
        Members:
        
          Undefined : Undefined
        
          Sun : Sun
        
          Mercury : Mercury
        
          Venus : Venus
        
          Earth : Earth
        
          Moon : Moon
        
          Mars : Mars
        
          Jupiter : Jupiter
        
          Saturn : Saturn
        
          Uranus : Uranus
        
          Neptune : Neptune
        """
        Earth: typing.ClassVar[SPICE.Object]  # value = <Object.Earth: 4>
        Jupiter: typing.ClassVar[SPICE.Object]  # value = <Object.Jupiter: 7>
        Mars: typing.ClassVar[SPICE.Object]  # value = <Object.Mars: 6>
        Mercury: typing.ClassVar[SPICE.Object]  # value = <Object.Mercury: 2>
        Moon: typing.ClassVar[SPICE.Object]  # value = <Object.Moon: 5>
        Neptune: typing.ClassVar[SPICE.Object]  # value = <Object.Neptune: 10>
        Saturn: typing.ClassVar[SPICE.Object]  # value = <Object.Saturn: 8>
        Sun: typing.ClassVar[SPICE.Object]  # value = <Object.Sun: 1>
        Undefined: typing.ClassVar[SPICE.Object]  # value = <Object.Undefined: 0>
        Uranus: typing.ClassVar[SPICE.Object]  # value = <Object.Uranus: 9>
        Venus: typing.ClassVar[SPICE.Object]  # value = <Object.Venus: 3>
        __members__: typing.ClassVar[dict[str, SPICE.Object]]  # value = {'Undefined': <Object.Undefined: 0>, 'Sun': <Object.Sun: 1>, 'Mercury': <Object.Mercury: 2>, 'Venus': <Object.Venus: 3>, 'Earth': <Object.Earth: 4>, 'Moon': <Object.Moon: 5>, 'Mars': <Object.Mars: 6>, 'Jupiter': <Object.Jupiter: 7>, 'Saturn': <Object.Saturn: 8>, 'Uranus': <Object.Uranus: 9>, 'Neptune': <Object.Neptune: 10>}
        def __eq__(self, other: typing.Any) -> bool:
            ...
        def __getstate__(self) -> int:
            ...
        def __hash__(self) -> int:
            ...
        def __index__(self) -> int:
            ...
        def __init__(self, value: int) -> None:
            ...
        def __int__(self) -> int:
            ...
        def __ne__(self, other: typing.Any) -> bool:
            ...
        def __repr__(self) -> str:
            ...
        def __setstate__(self, state: int) -> None:
            ...
        def __str__(self) -> str:
            ...
        @property
        def name(self) -> str:
            ...
        @property
        def value(self) -> int:
            ...
    @staticmethod
    def string_from_object(object: SPICE.Object) -> ostk.core.type.String:
        """
                        Convert a SPICE object to its string representation.
        
                        Args:
                            object (SPICE.Object): The SPICE object.
        
                        Returns:
                            str: String representation of the SPICE object.
        """
    def __init__(self, object: SPICE.Object) -> None:
        """
                        Constructor.
        
                        Args:
                            object (SPICE.Object): The SPICE object for this ephemeris.
        """
