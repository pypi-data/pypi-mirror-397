from __future__ import annotations
import ostk.core.filesystem
import ostk.core.type
import ostk.physics
import ostk.physics.coordinate
import ostk.physics.environment.ephemeris
import typing
__all__ = ['Engine', 'Kernel', 'Manager']
class Engine:
    """
    
                SPICE Toolkit engine.
    
                The Engine is a singleton that manages SPICE kernel loading and provides
                access to SPICE functionality. It handles kernel loading/unloading and
                provides frame information for SPICE objects.
    
                Note:
                    This class is a singleton. Use Engine.get() to access the instance.
    
                Example:
                    >>> from ostk.physics.environment.ephemeris.spice import Engine
                    >>> engine = Engine.get()
                    >>> engine.reset()
            
    """
    @staticmethod
    def default_kernels() -> list[Kernel]:
        """
                        Get the default kernels.
        
                        Returns:
                            list[Kernel]: The default kernels.
        """
    @staticmethod
    def get() -> Engine:
        """
                        Get the engine singleton.
        
                        Returns:
                            Engine: Reference to the engine singleton.
        """
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def get_frame_of(self, spice_object: ostk.physics.environment.ephemeris.SPICE.Object) -> ostk.physics.coordinate.Frame:
        """
                        Get the reference frame of a SPICE object.
        
                        Args:
                            spice_object (SPICE.Object): The SPICE object.
        
                        Returns:
                            Frame: The reference frame of the SPICE object.
        """
    def get_kernels(self) -> list[Kernel]:
        """
                        Get a list of the loaded kernels.
        
                        Returns:
                            list[Kernel]: The kernels.
        """
    @typing.overload
    def is_kernel_loaded(self, kernel: Kernel) -> bool:
        """
                        Check if the provided kernel is loaded.
        
                        Args:
                            kernel (Kernel): The kernel to check.
        
                        Returns:
                            bool: True if the kernel is loaded, False otherwise.
        """
    @typing.overload
    def is_kernel_loaded(self, pattern: ostk.core.type.String) -> bool:
        """
                        Check if a kernel matching the provided pattern is loaded.
        
                        Args:
                            pattern (str): The regex pattern to check.
        
                        Returns:
                            bool: True if the kernel is loaded, False otherwise.
        """
    def load_kernel(self, kernel: Kernel) -> None:
        """
                        Load a kernel.
        
                        Args:
                            kernel (Kernel): The kernel to load.
        """
    def reset(self) -> None:
        """
                        Reset the engine.
        
                        Unloads all kernels and clears the cache.
        """
    def unload_all_kernels(self) -> None:
        """
                        Unload all kernels.
        
                        Unloads all kernels and clears the cache.
        """
    def unload_kernel(self, kernel: Kernel) -> None:
        """
                        Unload a kernel.
        
                        Args:
                            kernel (Kernel): The kernel to unload.
        """
class Kernel:
    """
    
                SPICE Toolkit kernel.
    
                A generalized data class for SPICE kernel files. SPICE kernels contain
                various types of data including spacecraft clock data, leap seconds,
                physical constants, instrument parameters, frame definitions, events,
                and ephemeris data.
    
                See Also:
                    https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/info/intrdctn.html
            
    """
    class Type:
        """
        Members:
        
          Undefined : 
                        Undefined kernel type.
                    
        
          SCLK : 
                        Spacecraft clock kernels (text).
                    
        
          LSK : 
                        Leapseconds kernels (text).
                    
        
          PCK : 
                        Physical constants kernels (text).
                    
        
          IK : 
                        Instrument parameter kernels (text).
                    
        
          FK : 
                        Frame definition kernels (text).
                    
        
          EK : 
                        E-kernels (text).
                    
        
          MK : 
                        Meta-kernels (text).
                    
        
          SPK : 
                        SP-kernels (binary) - Spacecraft and Planet ephemeris.
                    
        
          BPCK : 
                        Physical constants kernels (binary).
                    
        
          CK : 
                        C-kernels (binary) - Spacecraft orientation.
                    
        
          BEK : 
                        Events kernels (binary).
                    
        """
        BEK: typing.ClassVar[Kernel.Type]  # value = <Type.BEK: 11>
        BPCK: typing.ClassVar[Kernel.Type]  # value = <Type.BPCK: 9>
        CK: typing.ClassVar[Kernel.Type]  # value = <Type.CK: 10>
        EK: typing.ClassVar[Kernel.Type]  # value = <Type.EK: 6>
        FK: typing.ClassVar[Kernel.Type]  # value = <Type.FK: 5>
        IK: typing.ClassVar[Kernel.Type]  # value = <Type.IK: 4>
        LSK: typing.ClassVar[Kernel.Type]  # value = <Type.LSK: 2>
        MK: typing.ClassVar[Kernel.Type]  # value = <Type.MK: 7>
        PCK: typing.ClassVar[Kernel.Type]  # value = <Type.PCK: 3>
        SCLK: typing.ClassVar[Kernel.Type]  # value = <Type.SCLK: 1>
        SPK: typing.ClassVar[Kernel.Type]  # value = <Type.SPK: 8>
        Undefined: typing.ClassVar[Kernel.Type]  # value = <Type.Undefined: 0>
        __members__: typing.ClassVar[dict[str, Kernel.Type]]  # value = {'Undefined': <Type.Undefined: 0>, 'SCLK': <Type.SCLK: 1>, 'LSK': <Type.LSK: 2>, 'PCK': <Type.PCK: 3>, 'IK': <Type.IK: 4>, 'FK': <Type.FK: 5>, 'EK': <Type.EK: 6>, 'MK': <Type.MK: 7>, 'SPK': <Type.SPK: 8>, 'BPCK': <Type.BPCK: 9>, 'CK': <Type.CK: 10>, 'BEK': <Type.BEK: 11>}
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
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def file(file: ostk.core.filesystem.File) -> Kernel:
        """
                        Create a kernel from a file.
        
                        The kernel type is automatically determined from the file extension.
        
                        Args:
                            file (File): The kernel file.
        
                        Returns:
                            Kernel: A kernel object.
        """
    @staticmethod
    def string_from_type(type: Kernel.Type) -> ostk.core.type.String:
        """
                        Convert a kernel type to string.
        
                        Args:
                            type (Kernel.Type): The kernel type.
        
                        Returns:
                            str: The string representation of the kernel type.
        """
    @staticmethod
    def type_from_file_extension(file_extension: ostk.core.type.String) -> Kernel.Type:
        """
                        Convert a file extension to a kernel type.
        
                        Args:
                            file_extension (str): The file extension.
        
                        Returns:
                            Kernel.Type: The kernel type.
        """
    @staticmethod
    def type_from_string(string: ostk.core.type.String) -> Kernel.Type:
        """
                        Convert a string to a kernel type.
        
                        Args:
                            string (str): The kernel type string.
        
                        Returns:
                            Kernel.Type: The kernel type.
        """
    @staticmethod
    def undefined() -> Kernel:
        """
                        Create an undefined kernel.
        
                        Returns:
                            Kernel: An undefined kernel.
        """
    def __eq__(self, arg0: Kernel) -> bool:
        ...
    def __init__(self, type: Kernel.Type, file: ostk.core.filesystem.File) -> None:
        """
                        Constructor.
        
                        Args:
                            type (Kernel.Type): The kernel type.
                            file (File): The kernel file.
        """
    def __ne__(self, arg0: Kernel) -> bool:
        ...
    def get_file(self) -> ostk.core.filesystem.File:
        """
                        Get the kernel file.
        
                        Returns:
                            File: The kernel file.
        """
    def get_name(self) -> ostk.core.type.String:
        """
                        Get the kernel name.
        
                        Returns:
                            str: The kernel name.
        """
    def get_type(self) -> Kernel.Type:
        """
                        Get the kernel type.
        
                        Returns:
                            Kernel.Type: The kernel type.
        """
    def is_defined(self) -> bool:
        """
                        Check if the kernel is defined.
        
                        Returns:
                            bool: True if the kernel is defined, False otherwise.
        """
class Manager(ostk.physics.Manager):
    """
    
                SPICE Toolkit kernel manager.
    
                Fetches and manages SPICE kernels. The manager can operate in two modes:
                - Automatic: Fetches kernels from remote repositories if not present locally.
                - Manual: Only uses locally available kernels.
    
                The following environment variables can be defined:
                - "OSTK_PHYSICS_ENVIRONMENT_EPHEMERIS_SPICE_MANAGER_MODE" overrides the default mode.
                - "OSTK_PHYSICS_ENVIRONMENT_EPHEMERIS_SPICE_MANAGER_LOCAL_REPOSITORY" overrides the default local repository.
    
                Note:
                    This class is a singleton. Use Manager.get() to access the instance.
    
                Example:
                    >>> from ostk.physics.environment.ephemeris.spice import Manager
                    >>> manager = Manager.get()
                    >>> manager.get_mode()
            
    """
    @staticmethod
    def get() -> Manager:
        """
                        Get the manager singleton.
        
                        Returns:
                            Manager: Reference to the manager singleton.
        """
    def fetch_kernel(self, kernel: Kernel) -> None:
        """
                        Fetch a kernel from the remote repository.
        
                        Args:
                            kernel (Kernel): The kernel to fetch.
        """
    def fetch_matching_kernels(self, regex_string: ostk.core.type.String) -> list[Kernel]:
        """
                        Fetch kernels matching a regular expression.
        
                        Args:
                            regex_string (str): A regular expression to match kernel names.
        
                        Returns:
                            list[Kernel]: An array of matching kernels.
        """
    def find_kernel(self, regex_string: ostk.core.type.String) -> Kernel:
        """
                        Find a kernel matching a regular expression.
        
                        Searches locally first, then remotely. Always returns the first match.
        
                        Args:
                            regex_string (str): A regular expression to match kernel names.
        
                        Returns:
                            Kernel: The first matching kernel.
        """
    def find_kernel_paths(self, regex_string: ostk.core.type.String) -> list[ostk.core.filesystem.Path]:
        """
                        Find kernel paths matching a regular expression in the local repository.
        
                        Args:
                            regex_string (str): A regular expression to match kernel paths.
        
                        Returns:
                            list[Path]: An array of matching kernel paths.
        """
