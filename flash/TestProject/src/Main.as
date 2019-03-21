package
{
	import flash.display.FrameLabel;
	import flash.display.Sprite;
	import flash.display.StageScaleMode;
	import flash.display.StageAlign;
	import flash.events.Event;
	import flash.text.TextField;
	import flash.text.TextFieldAutoSize;
	import flash.text.TextFormat;
	import flash.text.TextFormatAlign;
	import flash.filters.DropShadowFilter;
	import LabelContainer;
	import PanelContainer;
	
	/**
	 * ...
	 * @author Chirimen
	 */
	public class Main extends Sprite 
	{
		public var fieldWidth:int = 0;
		public var fieldHeight:int = 0;
		
		private var panel:PanelContainer;
		
		public function Main() 
		{
			if (stage) init();
			else addEventListener(Event.ADDED_TO_STAGE, init);
		}
		
		private function init(e:Event = null):void 
		{
			removeEventListener(Event.ADDED_TO_STAGE, init);
			// entry point
			stage.scaleMode = StageScaleMode.NO_SCALE;
			stage.align = StageAlign.TOP_LEFT;
			
			//test();
		}
				
		public function as_createPanel(config:Array, style:Object):void
		{
			panel = new PanelContainer(config, style);
			stage.addChild(panel);
			fieldWidth = panel.fieldWidth;
			fieldHeight = panel.fieldHeight;
			panel.alpha = style.alpha;
		}
		
		public function as_setValue(name:String = null, text:String = null):void
		{
			var child:LabelContainer = panel.getChildByName(name) as LabelContainer;
			child.valueField.text = text;
		}

		public function as_setPosition(x:int = 0, y:int = 0):void
		{
			panel.x = x;
			panel.y = y;
		}
		
		public function test():void
		{
			var config:Array = [
				{
					"name":         "test",
					"label":        "Test",
					'unit':         "(suffix)"
				},
				{
					"name":         "test",
					"label":        "Test",
					'unit':         "(suffix)"
				}
			];
			var style:Object = {
				"font": 			"default_small.font",
				"fontsize":			14,
				"statsWidth": 		150,
				"alpha": 			0.8,
				"panel_offset": 	[ -200, -20],
				"horizontalAnchor":	"RIGHT",
				"verticalAnchor": 	"TOP",
				"colour": 			[255, 255, 0],
				"backgroundColor": 	[0, 0, 0, 0.4],
				"paddingTop": 		4,
				"paddingBottom": 	4,
				"paddingLeft": 		4,
				"paddingRight": 	4,
				"lineHeight": 		18,
				"textColor": 		[255, 255, 0]				
			};
			as_createPanel(config, style)
		}
		
	}
	
}
