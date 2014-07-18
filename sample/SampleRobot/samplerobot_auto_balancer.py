#!/usr/bin/env python

try:
    from hrpsys.hrpsys_config import *
    import OpenHRP
except:
    print "import without hrpsys"
    import rtm
    from rtm import *
    from OpenHRP import *
    import waitInput
    from waitInput import *
    import socket
    import time

def getRTCList ():
    return [
            ['seq', "SequencePlayer"],
            ['sh', "StateHolder"],
            ['fk', "ForwardKinematics"],
            ['abc', "AutoBalancer"],
            ]

def init ():
    global hcf
    hcf = HrpsysConfigurator()
    hcf.getRTCList = getRTCList
    hcf.init ("SampleRobot(Robot)0")

def demo():
    init()
    # set initial pose from sample/controller/SampleController/etc/Sample.pos
    initial_pose = [-7.779e-005,  -0.378613,  -0.000209793,  0.832038,  -0.452564,  0.000244781,  0.31129,  -0.159481,  -0.115399,  -0.636277,  0,  0,  0,  -7.77902e-005,  -0.378613,  -0.000209794,  0.832038,  -0.452564,  0.000244781,  0.31129,  0.159481,  0.115399,  -0.636277,  0,  0,  0,  0,  0,  0]
    arm_front_pose = [-7.779e-005,  -0.378613,  -0.000209793,  0.832038,  -0.452564,  0.000244781, -0.8,  -0.159481,  -0.115399,  -0.636277,  0,  0,  0,  -7.77902e-005,  -0.378613,  -0.000209794,  0.832038,  -0.452564,  0.000244781,  -0.8,  0.159481,  0.115399,  -0.636277,  0,  0,  0,  0.2,  0,  0]
    hcf.seq_svc.setJointAngles(initial_pose, 2.0)
    hcf.seq_svc.waitInterpolation()

    # sample for AutoBalancer mode
    #   1. AutoBalancer mode by fixing feet
    hcf.abc_svc.startAutoBalancer([":rleg", ":lleg"]);
    hcf.seq_svc.setJointAngles(arm_front_pose, 1.0)
    hcf.seq_svc.waitInterpolation()
    hcf.seq_svc.setJointAngles(initial_pose, 1.0)
    hcf.seq_svc.waitInterpolation()
    hcf.abc_svc.stopAutoBalancer();
    #   2. AutoBalancer mode by fixing hands and feet
    hcf.abc_svc.startAutoBalancer([":rleg", ":lleg", ":rarm", ":larm"])
    hcf.seq_svc.setJointAngles(arm_front_pose, 1.0)
    hcf.seq_svc.waitInterpolation()
    hcf.seq_svc.setJointAngles(initial_pose, 1.0)
    hcf.seq_svc.waitInterpolation()
    hcf.abc_svc.stopAutoBalancer();
    #   3. getAutoBalancerParam
    ret = hcf.abc_svc.getAutoBalancerParam()
    if ret[0]:
        print "getAutoBalancerParam() => OK"
    #   4. setAutoBalancerParam
    ret[1].default_zmp_offsets = [[0.1,0,0], [0.1,0,0]]
    hcf.abc_svc.setAutoBalancerParam(ret[1])
    if ret[0] and ret[1].default_zmp_offsets == [[0.1,0,0], [0.1,0,0]]:
        print "setAutoBalancerParam() => OK"
    hcf.abc_svc.startAutoBalancer([":rleg", ":lleg"]);
    hcf.abc_svc.stopAutoBalancer();
    ret[1].default_zmp_offsets = [[0,0,0], [0,0,0]]
    hcf.abc_svc.setAutoBalancerParam(ret[1])

    # sample for walk pattern generation by AutoBalancer RTC
    #   1. goPos
    hcf.abc_svc.goPos(0.1, 0.05, 20)
    hcf.abc_svc.waitFootSteps()
    #   2. goVelocity and goStop
    hcf.abc_svc.goVelocity(-0.1, -0.05, -20)
    time.sleep(1)
    hcf.abc_svc.goStop()
    #   3. setFootSteps
    hcf.abc_svc.setFootSteps([OpenHRP.AutoBalancerService.Footstep([0,-0.09,0], [1,0,0,0], ":rleg"), OpenHRP.AutoBalancerService.Footstep([0,0.09,0], [1,0,0,0], ":lleg")])
    hcf.abc_svc.waitFootSteps()
    hcf.abc_svc.setFootSteps([OpenHRP.AutoBalancerService.Footstep([0,-0.09,0], [1,0,0,0], ":rleg"), OpenHRP.AutoBalancerService.Footstep([0.15,0.09,0], [1,0,0,0], ":lleg"), OpenHRP.AutoBalancerService.Footstep([0.3,-0.09,0], [1,0,0,0], ":rleg"), OpenHRP.AutoBalancerService.Footstep([0.3,0.09,0], [1,0,0,0], ":lleg")])
    hcf.abc_svc.waitFootSteps()
    #   4. getGaitGeneratorParam
    ret1 = hcf.abc_svc.getGaitGeneratorParam()
    if ret1[0]:
        print "getGaitGeneratorParam() => OK"
    #   5. setGaitGeneratorParam
    newparam = hcf.abc_svc.getGaitGeneratorParam()
    newparam[1].default_step_time = 0.7
    newparam[1].default_step_height = 0.15
    newparam[1].default_double_support_ratio = 0.4
    newparam[1].default_orbit_type = OpenHRP.AutoBalancerService.RECTANGLE;
    hcf.abc_svc.setGaitGeneratorParam(newparam[1])
    ret2 = hcf.abc_svc.getGaitGeneratorParam()
    if ret2[0] and ret2[1].default_step_time == newparam[1].default_step_time and ret2[1].default_step_height == newparam[1].default_step_height and ret2[1].default_double_support_ratio == newparam[1].default_double_support_ratio and ret2[1].default_orbit_type == newparam[1].default_orbit_type:
        print "setGaitGeneratorParam() => OK"
    hcf.abc_svc.goVelocity(0.1,0,0)
    time.sleep(1)
    hcf.abc_svc.goStop()
    hcf.abc_svc.setGaitGeneratorParam(ret1[1]) # revert parameter
    #  6. non-default stride
    hcf.abc_svc.startAutoBalancer([":rleg", ":lleg"]);
    hcf.abc_svc.setFootSteps([OpenHRP.AutoBalancerService.Footstep([0,-0.09,0], [1,0,0,0], ":rleg"), OpenHRP.AutoBalancerService.Footstep([0.15,0.09,0], [1,0,0,0], ":lleg")])
    hcf.abc_svc.waitFootSteps()
    hcf.abc_svc.setFootSteps([OpenHRP.AutoBalancerService.Footstep([0,-0.09,0], [1,0,0,0], ":rleg"), OpenHRP.AutoBalancerService.Footstep([0,0.09,0], [1,0,0,0], ":lleg")])
    hcf.abc_svc.waitFootSteps()
    hcf.abc_svc.stopAutoBalancer();
    #  7. walking by fixing 
    # abc_svc.startAutoBalancer([AutoBalancerService.AutoBalancerLimbParam(":rleg", [0,0,0], [0,0,0,0]),
    #                   AutoBalancerService.AutoBalancerLimbParam(":lleg", [0,0,0], [0,0,0,0]),
    #                   AutoBalancerService.AutoBalancerLimbParam(":rarm", [0,0,0], [0,0,0,0]),
    #                   AutoBalancerService.AutoBalancerLimbParam(":larm", [0,0,0], [0,0,0,0])])
    # abc_svc.goPos(0.1, 0.05, 20)
    # abc_svc.waitFootSteps()
    # abc_svc.stopABC()
