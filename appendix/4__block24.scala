import com.amazon.deequ.suggestions.{ConstraintSuggestionRunner, Rules}
import scala.collection.JavaConverters._

// 生成约束建议
val suggestionResult = {
  ConstraintSuggestionRunner()
    .onData(df)
    .addConstraintRules(Rules.DEFAULT)
    .run()
}

// 输出约束建议
println("自动生成的约束建议：")
suggestionResult.constraintSuggestions.foreach {
  suggestion =>
    println(s"  - 列名: ${suggestion.columnName}")
    println(s"    建议约束: ${suggestion.description}")
    println(s"    代码实现: ${suggestion.codeForConstraint}")
    println(s"    原因: ${suggestion.reason.getOrElse("")}")
}

// 应用建议的约束
val suggestedConstraints = suggestionResult.constraintSuggestions
  .map(_.constraint)
  .asJava

val verificationResultWithSuggestions = {
  VerificationSuite()
    .onData(df)
    .addCheck(
      Check(CheckLevel.Warning, "自动建议的约束")
        .addConstraints(suggestedConstraints)
    )
    .run()
}
