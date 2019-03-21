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
		private var text1:TextField = new TextField();
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
			
			text1.autoSize = TextFieldAutoSize.LEFT;
			text1.defaultTextFormat = new TextFormat("$FieldFont", 16, 0xffff00);
			text1.alpha = 0.8
			
			var dropShadow:DropShadowFilter = new DropShadowFilter(0, 45, 0, 0.8, 8, 8, 3);
			text1.filters = [ dropShadow ];
			text1.x = 100;
			text1.y = 100;
			text1.text = "TEST";
			
			stage.addChild(text1);
		}
				
		public function as_createPanel(config:Array):void
		{
			var dropShadow:DropShadowFilter = new DropShadowFilter(0, 45, 0, 0.8, 8, 8, 3);
			var filters:Array = [ dropShadow ];
			panel = new PanelContainer(config, filters);
			stage.addChild(panel);
		}
		
		public function as_setText(text:String = null):void
		{
			text1.htmlText = text;
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
		
	}
	
}
