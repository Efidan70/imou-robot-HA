import hashlib, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))


def test_sign_vector():
    from custom_components.imou_robot.api import calc_sign
    assert calc_sign(1706511734, "f5a1ae2d-c09c-4d39-a744-83a5c2c653c2",
                     "test123456789test123456789") == "xjhCQBoJ9hRDsCjyDcHjtDNzRZ3ZJezcawsfWeiaoxU="


def test_platforms_import():
    import custom_components.imou_robot.vacuum as v
    import custom_components.imou_robot.sensor as s
    import custom_components.imou_robot as init
    assert v.FEATURES and s.ImouSensor and init.PLATFORMS
