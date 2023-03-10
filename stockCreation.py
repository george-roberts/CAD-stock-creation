# Author-George Roberts
# Description-Creating stock and fixtures

import adsk.core
import adsk.fusion
import traceback
import math

deafultStockType = "Relative Size Box"

# global set of event handlers to keep them referenced for the duration of the command
handlers = []
app = adsk.core.Application.get()
if app:
    ui = app.userInterface

_inputs = adsk.core.CommandInputs.cast(None)
_angleInput = adsk.core.AngleValueCommandInput.cast(None)
_manipulationPoint = adsk.core.Point3D.create(0, 0, 0)
_cgGroups = adsk.fusion.CustomGraphicsGroups.cast(None)
_boxToCreate = []
_currentAngle = 0

class StockCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            global _inputs
            product = app.activeProduct
            design = adsk.fusion.Design.cast(product)
            if not design:
                ui.messageBox(
                'It is not supported in current workspace, please change to MODEL workspace and try again.')
                return
            if design.rootComponent.customGraphicsGroups.count > 0:
                design.rootComponent.customGraphicsGroups.item(0).deleteMe()
                app.activeViewport.refresh()
            global _cgGroups
            _cgGroups = design.rootComponent.customGraphicsGroups

            unitsMgr = app.activeProduct.unitsManager
            command = args.firingEvent.sender
            _inputs = command.commandInputs

            stock = Stock()
            offsets = [0,0,0,0,0,0]
            for input in _inputs:
                if input.id == 'stype':
                    stock.stockType = input.selectedItem.name
                if input.id == 'machinedParts':
                    numSelections = input.selectionCount
                    collSet = adsk.core.ObjectCollection.create()
                    for x in range(numSelections):
                        collSet.add(input.selection(x).entity)
                        stock.bodies = collSet
                if input.id == "slider":
                    stock.slider = input.valueOne
                if input.id == "angleVal":
                    stock.angleInp = input.value
                if input.id == "relAddXPos":
                    offsets[0] = input.value
                if input.id == "relAddXNeg":
                    offsets[1] = input.value
                if input.id == "relAddYPos":
                    offsets[2] = input.value
                if input.id == "relAddYNeg":
                    offsets[3] = input.value
                if input.id == "relAddZPos":
                    offsets[4] = input.value
                if input.id == "relAddZNeg":
                    offsets[5] = input.value
            stock.offsets = offsets
            stock.getBounds(args, True)
            args.isValidResult = True
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class inputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            global _inputs, _manipulationPoint
            unitsMgr = app.activeProduct.unitsManager
            command = args.firingEvent.sender
            _inputs = command.commandInputs
            stock = Stock()
            offsets = [0,0,0,0,0,0]
            for input in _inputs:
                if input.id == 'stype':
                    stock.stockType = input.selectedItem.name
                if input.id == 'machinedParts':
                    numSelections = input.selectionCount
                    collSet = adsk.core.ObjectCollection.create()
                    for x in range(numSelections):
                        collSet.add(input.selection(x).entity)
                        stock.bodies = collSet
                if input.id == "slider":
                    stock.slider = input.valueOne
                if input.id == "angleVal":
                    stock.angleInp = input.value
                if input.id == "relAddXPos":
                    offsets[0] = input.value
                if input.id == "relAddXNeg":
                    offsets[1] = input.value
                if input.id == "relAddYPos":
                    offsets[2] = input.value
                if input.id == "relAddYNeg":
                    offsets[3] = input.value
                if input.id == "relAddZPos":
                    offsets[4] = input.value
                if input.id == "relAddZNeg":
                    offsets[5] = input.value
            stock.offsets = offsets
            bounds = stock.getBounds(args, False)
            xSize = round(abs(bounds.maxPoint.x - bounds.minPoint.x) + offsets[0] + offsets[1], 4) * 10
            ySize = round(abs(bounds.maxPoint.y - bounds.minPoint.y) + offsets[2] + offsets[3], 4) * 10
            zSize = round(abs(bounds.maxPoint.z - bounds.minPoint.z) + offsets[4] + offsets[5], 4) * 10
            _inputs.itemById('sizeInfo').formattedText = 'X:' + str(xSize) + '\nY:' + str(ySize) + '\nZ:' + str(zSize)
            setFormVisibilities(bounds, stock.angleInp, args)

            for input in _inputs:
                if input.id == 'stype':
                    #stock.stockType = input.selectedItem.name
                    a = 1
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def setFormVisibilities(bounds, angle, args):
    global _manipulationPoint
    if not bounds.minPoint.x == 0 and not bounds.maxPoint.x == 0:
        command = args.firingEvent.sender
        _inputs = command.commandInputs
        angleManip = _inputs.itemById("angleVal")
        angleManip.isVisible = True
        angleManip.setManipulator(_manipulationPoint, adsk.core.Vector3D.create(1, 0, 0), adsk.core.Vector3D.create(0, 1, 0))
        
        additionalXPos = _inputs.itemById("relAddXPos")
        xPosDir = adsk.core.Vector3D.create(1, 0, 0)
        point = adsk.core.Point3D.create(bounds.maxPoint.x, _manipulationPoint.y, bounds.minPoint.z + ((bounds.maxPoint.z - bounds.minPoint.z) / 2))
        setDirectionManipulator(additionalXPos, point, angle, xPosDir)

        additionalXNeg = _inputs.itemById("relAddXNeg")
        xPosDir = adsk.core.Vector3D.create(-1, 0, 0)
        point = adsk.core.Point3D.create(bounds.minPoint.x, _manipulationPoint.y, bounds.minPoint.z + ((bounds.maxPoint.z - bounds.minPoint.z) / 2))
        setDirectionManipulator(additionalXNeg, point, angle, xPosDir)
        
        additionalYPos = _inputs.itemById("relAddYPos")
        xPosDir = adsk.core.Vector3D.create(0, 1, 0)
        point = adsk.core.Point3D.create(_manipulationPoint.x, bounds.maxPoint.y, bounds.minPoint.z + ((bounds.maxPoint.z - bounds.minPoint.z) / 2))
        setDirectionManipulator(additionalYPos, point, angle, xPosDir)

        additionalYNeg = _inputs.itemById("relAddYNeg")
        xPosDir = adsk.core.Vector3D.create(0, -1, 0)
        point = adsk.core.Point3D.create(_manipulationPoint.x, bounds.minPoint.y, bounds.minPoint.z + ((bounds.maxPoint.z - bounds.minPoint.z) / 2))
        setDirectionManipulator(additionalYNeg, point, angle, xPosDir)      

        additionalZPos = _inputs.itemById("relAddZPos")
        zPosDir = adsk.core.Vector3D.create(0, 0, 1)
        point = adsk.core.Point3D.create(_manipulationPoint.x, _manipulationPoint.y, bounds.maxPoint.z)
        setDirectionManipulator(additionalZPos, point, angle, zPosDir)

        additionalZNeg = _inputs.itemById("relAddZNeg")
        zNegDir = adsk.core.Vector3D.create(0, 0, -1)
        point = adsk.core.Point3D.create(_manipulationPoint.x, _manipulationPoint.y, bounds.minPoint.z)
        setDirectionManipulator(additionalZNeg, point, angle, zNegDir)
                
def setDirectionManipulator(manip, originPoint, angle, direction):
    manip.isVisible = True
    rotX = adsk.core.Matrix3D.create()
    rotX.setToRotation(angle, adsk.core.Vector3D.create(0,0,1), adsk.core.Point3D.create(_manipulationPoint.x, _manipulationPoint.y, _manipulationPoint.z))
    originPoint.transformBy(rotX)
    direction.transformBy(rotX)
    manip.setManipulator(originPoint, direction)

def makeStock():
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    rootComp = design.rootComponent
    
    ## get the points for the stock box
    box = _boxToCreate
    bottomLeft = adsk.core.Point3D.create(box[0], box[1], 0)
    bottomRight = adsk.core.Point3D.create(box[3], box[1], 0)
    topRight = adsk.core.Point3D.create(box[3], box[4], 0)
    topLeft = adsk.core.Point3D.create(box[0], box[4], 0)
    bottomHeight = box[2]
    topHeight = box[5]
    
    ## translate them based on the defined rotation
    rotation = adsk.core.Matrix3D.create()
    global _currentAngle
    rotation.setToRotation(_currentAngle, adsk.core.Vector3D.create(0, 0, 1), _manipulationPoint)
            
    bottomLeft.transformBy(rotation)
    bottomRight.transformBy(rotation)
    topRight.transformBy(rotation)
    topLeft.transformBy(rotation)


    #### build the construction plane
    xYPlane = rootComp.xYConstructionPlane
    planes = rootComp.constructionPlanes
    planeInp = planes.createInput()
    planeInp.setByOffset(xYPlane, adsk.core.ValueInput.createByReal(bottomHeight))
    plane = planes.add(planeInp)
    plane.name = "Stock base"

    ## add the sketch and draw the box
    sketches = rootComp.sketches
    sketch = sketches.add(plane)
    curves = sketch.sketchCurves
    lines = curves.sketchLines
    lines.addByTwoPoints(bottomLeft, bottomRight)
    lines.addByTwoPoints(bottomRight, topRight)
    lines.addByTwoPoints(topRight, topLeft)
    lines.addByTwoPoints(topLeft, bottomLeft)

    ### create the extrude
    extrudes = rootComp.features.extrudeFeatures
    extInp = extrudes.createInput(sketch.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    extentDist = adsk.core.ValueInput.createByReal(topHeight - bottomHeight)
    extInp.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(extentDist), adsk.fusion.ExtentDirections.PositiveExtentDirection)
    bodyAdded = extrudes.add(extInp)
    bodyAdded = bodyAdded.bodies.item(0)
    bodyAdded.name = "Stock"
    bodyAdded.opacity = 0.5
    appearances = design.appearances
    try:
        myColor = appearances.itemByName('StockColor')
        bodyAdded.appearance = myColor
    except:
        fusionMats = app.materialLibraries.itemByName('Fusion 360 Appearance Library')
        yellowCol = fusionMats.appearances.itemByName('Paint - Enamel Glossy (Yellow)')
        newColor = design.appearances.addByCopy(yellowCol, 'StockColor')
        for prop in newColor.appearanceProperties:
            if prop.name == 'Color':
                colorProp = adsk.core.ColorProperty.cast(prop)
                colorProp.value = adsk.core.Color.create(255, 255, 0, 0)
        bodyAdded.appearance = newColor
   

class StockCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            des = adsk.fusion.Design.cast(app.activeProduct)
            root = des.rootComponent

            if root.customGraphicsGroups.count > 0:
                root.customGraphicsGroups.item(0).deleteMe()
                app.activeViewport.refresh()
            command = args.firingEvent.sender
            if args.terminationReason == adsk.core.CommandTerminationReason.CompletedTerminationReason:
                makeStock()
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class StockCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            cmd = args.command
            cmd.isRepeatable = False
            onExecute = StockCommandExecuteHandler()
            cmd.execute.add(onExecute)
            onExecutePreview = StockCommandExecuteHandler()
            cmd.executePreview.add(onExecutePreview)
            onDestroy = StockCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            handlers.append(onDestroy)
            onInputChanged = inputChangedHandler()
            cmd.inputChanged.add(onInputChanged)

            # keep the handler referenced beyond this function
            handlers.append(onExecute)
            handlers.append(onExecutePreview)
            handlers.append(onInputChanged)

            # define the inputs
            global _inputs
            _inputs = cmd.commandInputs

            selectionInput = _inputs.addSelectionInput('machinedParts', 'Bodies', 'Select bodies')
            selectionInput.setSelectionLimits(0)
            selectionInput.addSelectionFilter("Bodies")
            selectionInput.addSelectionFilter("MeshBodies")

            _inputs.addTextBoxCommandInput('sizeInfo', 'Size', 'X:\nY:\nZ:', 3, True)
            additionalX = _inputs.addDistanceValueCommandInput("relAddXPos", "Offset X-", adsk.core.ValueInput.createByString('0 mm'))
            additionalX.isVisible = False
            additionalX = _inputs.addDistanceValueCommandInput("relAddXNeg", "Offset X-", adsk.core.ValueInput.createByString('0 mm'))
            additionalX.isVisible = False
            additionalY = _inputs.addDistanceValueCommandInput("relAddYPos", "Offset Y+", adsk.core.ValueInput.createByString('0 mm'))
            additionalY.isVisible = False
            additionalY = _inputs.addDistanceValueCommandInput("relAddYNeg", "Offset Y-", adsk.core.ValueInput.createByString('0 mm'))
            additionalY.isVisible = False
            additionalZ = _inputs.addDistanceValueCommandInput("relAddZPos", "Offset Z+", adsk.core.ValueInput.createByString('0 mm'))
            additionalZ.isVisible = False
            additionalZ = _inputs.addDistanceValueCommandInput("relAddZNeg", "Offset Z-", adsk.core.ValueInput.createByString('0 mm'))
            additionalZ.isVisible = False
        
            global _angleInput
            _angleInput = _inputs.addAngleValueCommandInput("angleVal", "Angle", adsk.core.ValueInput.createByString('0 degree'))
            _angleInput.isVisible = False

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class Stock:
    def __init__(self):
        self._stockType = deafultStockType
        self.bodies = adsk.core.ObjectCollection.create()

    # properties
    @property
    def stockType(self):
        return self._stockType

    @stockType.setter
    def stockType(self, value):
        self._stockType = value

    @property
    def bodies(self):
        return self._bodies

    @bodies.setter
    def bodies(self, value):
        self._bodies = value

    @property
    def slider(self):
        return self._slider

    @slider.setter
    def slider(self, value):
        self._slider = value
  
    @property
    def angleInp(self):
        return self._angleInp

    @angleInp.setter
    def angleInp(self, value):
        self._angleInp = value

    @property
    def offsets(self):
        return self._offsets

    @offsets.setter
    def offsets(self, value):
        self._offsets = value

    def getBounds(self, args, preview):
        global _manipulationPoint
        maxBoundingBox = adsk.core.BoundingBox3D.create(adsk.core.Point3D.create(0,0,0), adsk.core.Point3D.create(0,0,0))
        if self.bodies.count > 0:
            maxBoundingBox = self.bodies.item(0).boundingBox
            product = app.activeProduct
            design = adsk.fusion.Design.cast(product)
            rootComp = design.rootComponent
            brepMgr = adsk.fusion.TemporaryBRepManager.get()
            for x in range(self.bodies.count):
                maxBoundingBox.combine(self.bodies.item(x).boundingBox)
                
            _manipulationPoint = adsk.core.Point3D.create(
                maxBoundingBox.minPoint.x + ((maxBoundingBox.maxPoint.x - maxBoundingBox.minPoint.x) / 2),
                maxBoundingBox.minPoint.y + ((maxBoundingBox.maxPoint.y - maxBoundingBox.minPoint.y) / 2 ),
                maxBoundingBox.maxPoint.z
                )

            rotX = adsk.core.Matrix3D.create()
            rotX.setToRotation(-self.angleInp, adsk.core.Vector3D.create(0,0,1), _manipulationPoint)
            bod = brepMgr.copy(self.bodies.item(0))
            brepMgr.transform(bod,rotX)
            maxBoundingBox = bod.boundingBox
            for x in range(self.bodies.count):
                bod = brepMgr.copy(self.bodies.item(x))
                brepMgr.transform(bod, rotX)
                maxBoundingBox.combine(bod.boundingBox)
            newBoundBox = self.addOffsetToBox(maxBoundingBox)
            if preview:
                self.drawPreview(newBoundBox, self.angleInp)
            mp = newBoundBox.minPoint
            hp = newBoundBox.maxPoint
            global _boxToCreate, _currentAngle
            _boxToCreate = [mp.x, mp.y, mp.z, hp.x, hp.y, hp.z]
            _currentAngle = self.angleInp

        return maxBoundingBox

    def addOffsetToBox(self, maxBoundingBox):
        minPoint = adsk.core.Point3D.create(0, 0, 0)
        maxPoint = adsk.core.Point3D.create(0, 0, 0)
        minPoint.x = maxBoundingBox.minPoint.x - self.offsets[1]        
        maxPoint.x = maxBoundingBox.maxPoint.x + self.offsets[0]
        minPoint.y = maxBoundingBox.minPoint.y - self.offsets[3]
        maxPoint.y = maxBoundingBox.maxPoint.y + self.offsets[2]
        minPoint.z = maxBoundingBox.minPoint.z - self.offsets[5]
        maxPoint.z = maxBoundingBox.maxPoint.z + self.offsets[4]
        boundingBox = adsk.core.BoundingBox3D.create(minPoint, maxPoint)
        return boundingBox

    def drawPreview(self, maxBoundingBox, angle): 
        cgGroup = adsk.fusion.CustomGraphicsGroup.cast(_cgGroups.add())
        minP = maxBoundingBox.minPoint
        maxP = maxBoundingBox.maxPoint
        coords = []
        coords.extend([minP.x, minP.y, minP.z]) #0 bottom back left
        coords.extend([minP.x, minP.y, maxP.z]) #1 top back left
        coords.extend([minP.x, maxP.y, minP.z]) #2 bottom front left
        coords.extend([minP.x, maxP.y, maxP.z]) #3 top front left
        coords.extend([maxP.x, maxP.y, minP.z]) #4 bottom front right
        coords.extend([maxP.x, maxP.y, maxP.z]) #5 top front right 
        coords.extend([maxP.x, minP.y, minP.z]) #6 bottom back right
        coords.extend([maxP.x, minP.y, maxP.z]) #7 top back right
        triangle = [0,1,6, 1,7,6, 7,6,4, 7,4,5, 4,2,5, 5,2,3, 1,2,3, 0,1,2, 0,2,4, 0,6,4, 1,3,5, 5,1,7]
        vecs = adsk.fusion.CustomGraphicsCoordinates.create(coords)
        newMesh = cgGroup.addMesh(vecs, triangle, [], [])
        diffuse = adsk.core.Color.create(255, 255, 0, 255)
        ambient = adsk.core.Color.create(255, 255, 0, 255)
        specular = adsk.core.Color.create(255, 255, 0, 255)
        emissive = adsk.core.Color.create(255, 255, 0, 255)
        glossy = 0
        opacity = 0.4
        redBasicMaterial = adsk.fusion.CustomGraphicsBasicMaterialColorEffect.create(diffuse,ambient,specular,emissive,glossy,opacity)
        newMesh.color = redBasicMaterial
        lineArray = [
        minP.x, minP.y, minP.z, minP.x, minP.y, maxP.z,
        minP.x, maxP.y, maxP.z, minP.x, maxP.y, minP.z,
        minP.x, minP.y, minP.z, maxP.x, minP.y, minP.z,
        maxP.x, minP.y, maxP.z, minP.x, minP.y, maxP.z,
        minP.x, minP.y, minP.z, maxP.x, minP.y, minP.z,
        maxP.x, minP.y, maxP.z, maxP.x, maxP.y, maxP.z,
        maxP.x, maxP.y, minP.z, maxP.x, minP.y, minP.z,
        maxP.x, maxP.y, minP.z, minP.x, maxP.y, minP.z,
        minP.x, maxP.y, maxP.z, maxP.x, maxP.y, maxP.z
        ]
        lineCoords = adsk.fusion.CustomGraphicsCoordinates.create(lineArray)
        lines = cgGroup.addLines(lineCoords, [], True)
        rotX = adsk.core.Matrix3D.create()
        global _manipulationPoint
        rotX.setToRotation(angle, adsk.core.Vector3D.create(0,0,1), adsk.core.Point3D.create(_manipulationPoint.x, _manipulationPoint.y, _manipulationPoint.z))
        cgGroup.transform = rotX


def run(context):
    try:
        commandDefinitions = ui.commandDefinitions
        # check the command exists or not
        cmdDef = commandDefinitions.itemById('StockCreation')
        if not cmdDef:
            cmdDef = commandDefinitions.addButtonDefinition('StockCreation',
                                                            'Create Stock',
                                                            'Create stock body for a setup.',
                                                            './/Resources')  # relative resource file path is specified

        stockCommandCreated = StockCommandCreatedHandler()
        cmdDef.commandCreated.add(stockCommandCreated)
        handlers.append(stockCommandCreated)
        solidPanel = ui.allToolbarPanels.itemById('SolidCreatePanel')
        solidPanel.controls.addCommand(cmdDef)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def stop(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        if ui.commandDefinitions.itemById('StockCreation'):
            ui.commandDefinitions.itemById('StockCreation').deleteMe()
        solidPanel = ui.allToolbarPanels.itemById('SolidCreatePanel')
        cntrl = solidPanel.controls.itemById('StockCreation')
        if cntrl:
            cntrl.deleteMe()

        if cntrl:
            cntrl.deleteMe()
    except:
        pass