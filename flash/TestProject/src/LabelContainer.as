package 
{
	import flash.display.Sprite;
	import flash.text.TextField;
	import flash.text.TextFieldAutoSize;
	import flash.text.TextFormat;
	import flash.text.TextFormatAlign;
	import Math;
	
	/**
	 * ...
	 * @author Chirimen
	 */
	public class LabelContainer extends Sprite
	{
		private var labelField:TextField;
		private var valueField:TextField;
		private var unitField:TextField;
		
		public var anchorX:int = 0;
		public var anchorY:int = 0;
		public var fieldWidth:int = 0;
		public var fieldHeight:int = 0;

		public function LabelContainer()
		{
			var format:TextFormat;
			
			labelField = createTextField();
			labelField.autoSize = TextFieldAutoSize.LEFT;
			
			valueField = createTextField();
			valueField.autoSize = TextFieldAutoSize.NONE;
			
			unitField = createTextField();
			format = unitField.getTextFormat();
			format.align = TextFormatAlign.LEFT;
			unitField.defaultTextFormat = format;

			addChild(labelField);
			addChild(valueField);
			addChild(unitField);
		}
		
		private function createTextField():TextField
		{
			var textField:TextField = new TextField();
			var format:TextFormat = new TextFormat("$FieldFont", 16, 0xffff00);
			format.align = TextFormatAlign.RIGHT;
			textField.defaultTextFormat = format;
			return textField;
		}

		public function init(label:String, unit:String):void
		{
			labelField.x = 0;
			labelField.htmlText = label;
			
			var valueHeight:int;
			valueField.autoSize = TextFieldAutoSize.LEFT;
			valueField.text = "0";
			valueHeight = valueField.height;
			valueField.autoSize = TextFieldAutoSize.NONE;
			valueField.x = labelField.x + labelField.width;
			valueField.width = 180;
			valueField.height = valueHeight;
			valueField.htmlText = "";

			unitField.x = valueField.x + valueField.width;
			unitField.autoSize = TextFieldAutoSize.LEFT;
			unitField.htmlText = unit;

			anchorX = unitField.x
			anchorY = unitField.y
			valueField.htmlText = '(' + width + ',' + height + ')' + '(' + labelField.height + ',' + valueField.height + ',' + unitField.height + ')';
		}
		
		public function setValueText(text:String):void
		{
			valueField.htmlText = text;
		}
	}
	
}