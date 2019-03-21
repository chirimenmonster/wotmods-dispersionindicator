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
	public class LineContainer extends Sprite
	{
		public var labelField:TextField;
		public var valueField:TextField;
		public var unitField:TextField;
		
		public var anchorX:int = 0;
		public var anchorY:int = 0;
		public var fieldWidth:int = 0;
		public var fieldHeight:int = 0;

		public function LineContainer()
		{
			var format:TextFormat;
			
			labelField = new TextField();
			
			valueField = new TextField();
			valueField.autoSize = TextFieldAutoSize.NONE;
			
			unitField = new TextField();

			addChild(labelField);
			addChild(valueField);
			addChild(unitField);
		}
		
		private function getTextFormat(style:Object):TextFormat
		{
			var format:TextFormat = new TextFormat();
			format.font = style.font;
			format.size = style.fontsize;
			format.align = TextFormatAlign.RIGHT;
			if (style.hasOwnProperty("textColor"))
				format.color = style.textColor[0] << 16 + style.textColor[1] << 8 + style.textColor[2];
			format.color = 0xffff00;
			return format;
		}

		private function assignLabelField(textField:TextField, style:Object):void
		{
			var format:TextFormat = getTextFormat(style);
			format.align = TextFormatAlign.RIGHT;
			textField.defaultTextFormat = format;
			textField.autoSize = TextFieldAutoSize.LEFT;
		}

		private function assignValueField(textField:TextField, style:Object):void
		{
			var format:TextFormat = getTextFormat(style);
			format.align = TextFormatAlign.RIGHT;
			textField.defaultTextFormat = format;
			var height:int;
			textField.autoSize = TextFieldAutoSize.LEFT;
			textField.text = "0";
			height = textField.height;
			textField.text = "";
			textField.autoSize = TextFieldAutoSize.NONE;
			textField.width = style.statsWidth;
			textField.height = height;
		}
		
		private function assignUnitField(textField:TextField, style:Object):void
		{
			var format:TextFormat = getTextFormat(style);
			format.align = TextFormatAlign.LEFT;
			textField.defaultTextFormat = format;
			textField.autoSize = TextFieldAutoSize.LEFT;
		}
		
		public function init(label:String, unit:String, valueWidth:int, style:Object):void
		{
			assignLabelField(labelField, style);
			labelField.htmlText = label;
			labelField.x = 0;
			
			assignValueField(valueField, style);
			valueField.x = labelField.x + labelField.width;

			assignUnitField(unitField, style);
			
			unitField.x = valueField.x + valueField.width;
			unitField.htmlText = unit;

			anchorX = unitField.x
			anchorY = unitField.y
			valueField.htmlText = '(' + width + ',' + height + ')' + '(' + labelField.height + ',' + valueField.height + ',' + unitField.height + ')';
		}
		
		public function setFilters(filters:Array):void
		{
			labelField.filters = filters;
			valueField.filters = filters;
			unitField.filters = filters;
		}
		
		public function setValueText(text:String):void
		{
			valueField.htmlText = text;
		}
	}
	
}