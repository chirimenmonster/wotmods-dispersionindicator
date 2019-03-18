package
{
	import flash.display.Sprite;
	import flash.display.StageScaleMode;
	import flash.display.StageAlign;
	import flash.events.Event;
	import flash.text.TextField;
	import flash.text.TextFieldAutoSize;
	import flash.text.TextFormat;
	import flash.text.TextFormatAlign;
	import flash.filters.DropShadowFilter;
	
	/**
	 * ...
	 * @author Chirimen
	 */
	public class Main extends Sprite 
	{
		private var text1:TextField = new TextField();
		
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
			stage.addChild(text1);
			
			resizeHandler();
		}
		
		private function resizeHandler(e:Event = null):void {
			x = stage.stageWidth / 2;
			y = stage.stageHeight / 2;
			text1.htmlText = "Stage: (" + stage.stageWidth + ", " + stage.stageHeight + ")";
			text1.x = x - text1.width / 2;
			text1.y = y + 40;
		}
		
		public function as_setText(text:String = null):void {
			text1.htmlText = text;
		}

		public function as_setPosition(x:int = 0, y:int = 0):void {
			text1.x = x;
			text1.y = y;
		}
	}
}
