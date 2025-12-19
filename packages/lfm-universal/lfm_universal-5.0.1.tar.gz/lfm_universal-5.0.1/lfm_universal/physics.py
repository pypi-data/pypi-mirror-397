
class LFMConstants:
    ANCHOR_SCALE = 66
    VACUUM_PRESSURE = 1.0e32 
    MATTER_PRESSURE = 2.0e34 
    PRESSURE_DIFFERENTIAL = 200.0
    
    @staticmethod
    def validate_k(k):
        if k < 0 or k > 204:
            raise ValueError("Scale k must be within Universal Bounds (0-204)")
        return True
