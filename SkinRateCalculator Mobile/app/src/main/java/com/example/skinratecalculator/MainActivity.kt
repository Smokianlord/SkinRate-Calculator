package com.example.skinratecalculator

import android.os.Bundle
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawing
import androidx.compose.foundation.layout.windowInsetsPadding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Divider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.derivedStateOf
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalClipboardManager
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        setContent {
            SkinRateApp()
        }
    }
}

private val PageBg = Color(0xFF081014)
private val CardBg = Color(0xFF111B20)
private val CardSoft = Color(0xFF17252B)
private val Green = Color(0xFF22D37D)
private val TextMain = Color(0xFFEAF7F0)
private val TextMuted = Color(0xFF92A79C)
private val Border = Color(0xFF26363D)

@Composable
fun SkinRateApp() {
    MaterialTheme(
        colorScheme = darkColorScheme(
            background = PageBg,
            surface = CardBg,
            primary = Green,
            onBackground = TextMain,
            onSurface = TextMain,
            onPrimary = Color(0xFF04120B)
        )
    ) {
        Surface(
            modifier = Modifier.fillMaxSize(),
            color = PageBg
        ) {
            CalculatorScreen()
        }
    }
}

@Composable
fun CalculatorScreen() {
    var amountText by rememberSaveable { mutableStateOf("") }
    var itemRateText by rememberSaveable { mutableStateOf("") }
    var walletRateText by rememberSaveable { mutableStateOf("") }

    val amount = amountText.toDoubleOrNull() ?: 0.0
    val itemRate = itemRateText.toDoubleOrNull() ?: 0.0
    val walletRate = walletRateText.toDoubleOrNull() ?: 0.0

    val result by remember(amountText, itemRateText, walletRateText) {
        derivedStateOf {
            CalculatorResult(
                amount = amount,
                itemRate = itemRate,
                walletRate = walletRate
            )
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(PageBg)
            .windowInsetsPadding(WindowInsets.safeDrawing)
            .navigationBarsPadding()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 18.dp, vertical = 16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        HeaderCard()

        AppCard {
            Text(
                text = "Calculator",
                color = TextMain,
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold
            )

            Spacer(modifier = Modifier.height(14.dp))

            CleanInput(
                value = amountText,
                onValueChange = { amountText = it.cleanNumberInput() },
                label = "Amount in USD",
                placeholder = "Example: 100"
            )

            Spacer(modifier = Modifier.height(12.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                CleanInput(
                    value = itemRateText,
                    onValueChange = { itemRateText = it.cleanNumberInput() },
                    label = "Item rate",
                    placeholder = "120",
                    modifier = Modifier.weight(1f)
                )

                CleanInput(
                    value = walletRateText,
                    onValueChange = { walletRateText = it.cleanNumberInput() },
                    label = "Wallet rate",
                    placeholder = "110",
                    modifier = Modifier.weight(1f)
                )
            }

            Spacer(modifier = Modifier.height(16.dp))

            Button(
                onClick = {
                    amountText = ""
                    itemRateText = ""
                    walletRateText = ""
                },
                modifier = Modifier.fillMaxWidth(),
                colors = ButtonDefaults.buttonColors(
                    containerColor = Green,
                    contentColor = Color(0xFF03130B)
                ),
                shape = RoundedCornerShape(16.dp)
            ) {
                Text(
                    text = "Clear",
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.padding(vertical = 6.dp)
                )
            }
        }

        ResultCard(
            title = "Steam Tax",
            subtitle = "15% Steam tax estimate",
            rows = listOf(
                "With Steam Tax" to result.withSteamTax.money2(),
                "Without Steam Tax" to result.withoutSteamTax.money2()
            )
        )

        ResultCard(
            title = "Item Transfer",
            subtitle = "Amount × item rate",
            rows = listOf(
                "Transfer Cost" to result.itemCost.taka(),
                "Cashout Agent" to result.itemAgentCashout.taka(),
                "Cashout Priyo" to result.itemPriyoCashout.taka()
            )
        )

        ResultCard(
            title = "Wallet Transfer",
            subtitle = "Amount × wallet rate",
            rows = listOf(
                "Transfer Cost" to result.walletCost.taka(),
                "Cashout Agent" to result.walletAgentCashout.taka(),
                "Cashout Priyo" to result.walletPriyoCashout.taka()
            )
        )

        Text(
            text = "Agent cashout: 1.85%  •  Priyo cashout: 1.49%",
            color = TextMuted,
            fontSize = 12.sp,
            modifier = Modifier.padding(bottom = 18.dp)
        )
    }
}

@Composable
fun HeaderCard() {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .background(
                brush = Brush.linearGradient(
                    colors = listOf(
                        Color(0xFF153326),
                        Color(0xFF0D171B)
                    )
                ),
                shape = RoundedCornerShape(26.dp)
            )
            .padding(20.dp)
    ) {
        Column {
            Text(
                text = "Skin Rate Calculator",
                color = TextMain,
                fontSize = 25.sp,
                fontWeight = FontWeight.Bold
            )

            Spacer(modifier = Modifier.height(6.dp))

            Text(
                text = "Steam tax, item transfer, wallet transfer and cashout estimate",
                color = TextMuted,
                fontSize = 13.sp,
                lineHeight = 18.sp
            )
        }
    }
}

@Composable
fun AppCard(content: @Composable ColumnScope.() -> Unit) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(24.dp),
        colors = CardDefaults.cardColors(
            containerColor = CardBg
        ),
        elevation = CardDefaults.cardElevation(
            defaultElevation = 0.dp
        )
    ) {
        Column(
            modifier = Modifier.padding(18.dp),
            content = content
        )
    }
}

@Composable
fun CleanInput(
    value: String,
    onValueChange: (String) -> Unit,
    label: String,
    placeholder: String,
    modifier: Modifier = Modifier
) {
    OutlinedTextField(
        value = value,
        onValueChange = onValueChange,
        modifier = modifier.fillMaxWidth(),
        label = {
            Text(label)
        },
        placeholder = {
            Text(placeholder)
        },
        singleLine = true,
        keyboardOptions = KeyboardOptions(
            keyboardType = KeyboardType.Decimal
        ),
        shape = RoundedCornerShape(16.dp),
        colors = OutlinedTextFieldDefaults.colors(
            focusedTextColor = TextMain,
            unfocusedTextColor = TextMain,
            focusedBorderColor = Green,
            unfocusedBorderColor = Border,
            focusedLabelColor = Green,
            unfocusedLabelColor = TextMuted,
            cursorColor = Green,
            focusedContainerColor = Color(0xFF0E171B),
            unfocusedContainerColor = Color(0xFF0E171B),
            focusedPlaceholderColor = TextMuted,
            unfocusedPlaceholderColor = TextMuted
        )
    )
}

@Composable
fun ResultCard(
    title: String,
    subtitle: String,
    rows: List<Pair<String, String>>
) {
    AppCard {
        Text(
            text = title,
            color = TextMain,
            fontSize = 19.sp,
            fontWeight = FontWeight.Bold
        )

        Text(
            text = subtitle,
            color = TextMuted,
            fontSize = 12.sp
        )

        Spacer(modifier = Modifier.height(14.dp))

        rows.forEachIndexed { index, row ->
            ResultRow(
                label = row.first,
                value = row.second
            )

            if (index != rows.lastIndex) {
                Divider(
                    modifier = Modifier.padding(vertical = 10.dp),
                    color = Border
                )
            }
        }
    }
}

@Composable
fun ResultRow(
    label: String,
    value: String
) {
    val clipboard = LocalClipboardManager.current
    val context = LocalContext.current

    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Column(
            modifier = Modifier.weight(1f)
        ) {
            Text(
                text = label,
                color = TextMuted,
                fontSize = 13.sp
            )

            Spacer(modifier = Modifier.height(2.dp))

            Text(
                text = value,
                color = TextMain,
                fontSize = 21.sp,
                fontWeight = FontWeight.Bold
            )
        }

        Button(
            onClick = {
                clipboard.setText(AnnotatedString(value))
                Toast.makeText(context, "Copied: $value", Toast.LENGTH_SHORT).show()
            },
            colors = ButtonDefaults.buttonColors(
                containerColor = CardSoft,
                contentColor = Green
            ),
            shape = RoundedCornerShape(14.dp)
        ) {
            Text("Copy")
        }
    }
}

data class CalculatorResult(
    val amount: Double,
    val itemRate: Double,
    val walletRate: Double
) {
    val withSteamTax: Double = amount * 1.15
    val withoutSteamTax: Double = amount * 0.85

    val itemCost: Int = (amount * itemRate).toInt()
    val itemAgentCashout: Int = (itemCost * 1.0185).toInt()
    val itemPriyoCashout: Int = (itemCost * 1.0149).toInt()

    val walletCost: Int = (amount * walletRate).toInt()
    val walletAgentCashout: Int = (walletCost * 1.0185).toInt()
    val walletPriyoCashout: Int = (walletCost * 1.0149).toInt()
}

fun String.cleanNumberInput(): String {
    var dotUsed = false

    return buildString {
        for (char in this@cleanNumberInput) {
            if (char.isDigit()) {
                append(char)
            } else if (char == '.' && !dotUsed) {
                append(char)
                dotUsed = true
            }
        }
    }
}

fun Double.money2(): String {
    return "%.2f".format(this)
}

fun Int.taka(): String {
    return "৳$this"
}